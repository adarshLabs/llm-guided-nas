import os, re, json, random
from datetime import datetime, timezone
from pathlib import Path
from google import genai
from search_space import random_arch, ArchConfig, N_NODES, OPS
from nats_bench import create
from serializer import as_combined, as_adjacency, as_nats, as_prose
from dotenv import load_dotenv
from google.genai import types
load_dotenv()

MODEL = "gemini-3.5-flash-lite"
TEMPERATURE = 1.0
SEED = 42
LLM_SEED = None     # None = unseeded sampling. Set to an int to make calls repeatable.
MAX_QUERIES = 15     # distinct architectures the LLM may spend
MAX_CALLS   = 15    # hard stop, so duplicates cannot spin
LOG_PATH = Path("results/search_runs.jsonl")

# |op~src| repeated per group, groups joined by '+'.
ARCH_RE = re.compile(r"\|(?:\w+~\d\|)+(?:\+\|(?:\w+~\d\|)+)*")
HISTORY_NOTE = {
    as_nats:      "Each architecture below is given as that string.",
    as_adjacency: "Each architecture below is given as its six edges, one per line, as source -> target : operation. Line order carries no meaning.",
    as_prose:     "Each architecture below is described in words, one sentence per node.",
}

def parse_response(text, n_nodes=N_NODES):
    """Model output -> ArchConfig, or None if it is not a valid in-space cell.

    Never raises. Rejects: no text, no arch-shaped substring, parser blew up,
    wrong edge set, operation outside the space.
    """
    if not isinstance(text, str):
        return None
    m = ARCH_RE.search(text)
    if not m:
        return None
    try:
        arch = ArchConfig.from_arch_str(m.group(0))
    except Exception:
        return None
    expected = [[j, i] for i in range(1, n_nodes) for j in range(i)]
    if [[f, t] for f, t, _ in arch.edges] != expected:
        return None
    if any(op not in OPS for _, _, op in arch.edges):
        return None
    return arch


def build_prompt(arch_list, fmt=as_adjacency):
    history = "\n\n".join(
        f"Architecture {i + 1}: \n {as_combined(arch,acc, fmt)}"
        for i, (arch, acc) in enumerate(arch_list)
    )

    return f"""You are searching the NAS-Bench-201 cell space for the architecture with the highest CIFAR-10 test accuracy.
    A cell has 4 nodes. Node 0 is the input. Every node i receives one edge from every node j < i, so there are exactly 6 edges. Each edge carries exactly one operation from this set:
    {", ".join(OPS)}
    An architecture is written as a single string: the incoming edges of node 1, then node 2, then node 3, joined by "+". Within a group each edge is written operation~source_node, and every edge is wrapped in pipes.
    Example: |nor_conv_3x3~0|+|skip_connect~0|nor_conv_1x1~1|+|none~0|nor_conv_3x3~1|avg_pool_3x3~2|
    {HISTORY_NOTE[fmt]}
    Architectures already evaluated, with their measured accuracy:
    {history}
    Propose ONE new architecture that does not appear above and that you expect to score higher.
    Reply with the architecture string and nothing else. No explanation, no markdown, no code fences."""


def main():
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    api = create(None, 'tss', verbose=False, fast_mode=True)

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    #fmt_all = [as_prose, as_nats, as_adjacency]
    fmt = as_nats
    run_id = f"{datetime.now().strftime('%Y%m%dT%H%M%S')}-s{SEED}-{fmt.__name__}"

    def log(**fields):
        row = {
            "run_id": run_id,
            "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "sampler_seed": SEED,
            "llm_seed": LLM_SEED,
            "model": MODEL,
            "temperature": TEMPERATURE,
            "fmt": fmt.__name__,
            **fields,
        }
        with LOG_PATH.open("a") as f:
            f.write(json.dumps(row) + "\n")

    def accuracy_of(arch):
        arch_str = arch.to_arch_str()
        idx = api.query_index_by_arch(arch_str)
        if idx < 0:
            raise ValueError(f"arch string not in NATS-Bench: {arch_str}")
        acc = api.get_more_info(idx, 'cifar10', hp='200', is_random=False)['test-accuracy']
        api.clear_params(idx)
        return acc, idx


    random.seed(SEED)
    arch_list = []
    for n in range(5):
        arch = random_arch(N_NODES)
        acc, idx = accuracy_of(arch)
        arch_list.append((arch, acc))
        log(phase="seed", iteration=-1, arch_str=arch.to_arch_str(),
            idx=idx, accuracy=acc, parse_ok=True)

    prompt = build_prompt(arch_list, fmt)

    seen = {a.to_arch_str() for a, _ in arch_list}
    queries = calls = 0
    while queries< MAX_QUERIES and calls < MAX_CALLS:
        text = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=TEMPERATURE,
                                                seed=LLM_SEED)).text
        calls += 1

        result_arch = parse_response(text)
        if result_arch is None:
            print(f"iter {calls - 1}: PARSE FAIL <- {text[:90]!r}")
            log(phase="search", iteration=calls - 1, query=None, raw_response=text,
                arch_str=None, idx=None, accuracy=None, parse_ok=False)
            continue


        arch_str = result_arch.to_arch_str()
        if arch_str in seen:
            log(phase="search", iteration=calls - 1, query=None, raw_response=text,
                arch_str=arch_str, idx=None, accuracy=None,
                parse_ok=True, duplicate=True)
            continue

        seen.add(arch_str)
        queries += 1

        accuracy, idx = accuracy_of(result_arch)
        #print(text, idx, accuracy)
        log(phase="search", iteration=calls-1, query=queries, raw_response=text,
            arch_str=result_arch.to_arch_str(), idx=idx,
            accuracy=accuracy, parse_ok=True, duplicate=False)

        arch_list.append((result_arch, accuracy))
        prompt  = build_prompt(arch_list, fmt)

    log(phase="end", iteration=calls - 1, query=queries,
        stop_reason="budget" if queries >= MAX_QUERIES else "call_cap")

if __name__=="__main__":
    main()
