import os, re, json, random
from datetime import datetime, timezone
from pathlib import Path
from google import genai
from nats_bench import create
from search_space import random_arch, ArchConfig, N_NODES, OPS
from serializer import as_combined, as_adjacency
from dotenv import load_dotenv
from google.genai import types
from collections import deque
load_dotenv()

MODEL = "gemini-3.1-flash-lite"
TEMPERATURE = 1.0
SEED = 42
LOG_PATH = Path("results/search_runs.jsonl")

# |op~src| repeated per group, groups joined by '+'.
ARCH_RE = re.compile(r"\|(?:\w+~\d\|)+(?:\+\|(?:\w+~\d\|)+)*")


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


def build_prompt(arch_list):
    history = "\n\n".join(
        f"Architecture {i + 1}: \n {as_combined(arch,acc)}"
        for i, (arch, acc) in enumerate(arch_list)
    )

    return f"""You are searching the NAS-Bench-201 cell space for the architecture with the highest CIFAR-10 test accuracy.

    A cell has 4 nodes. Node 0 is the input. Every node i receives one edge from every node j < i, so there are exactly 6 edges. Each edge carries exactly one operation from this set:
    {", ".join(OPS)}

    An architecture is written as a single string: the incoming edges of node 1, then node 2, then node 3, joined by "+". Within a group each edge is written operation~source_node, and every edge is wrapped in pipes.

    Example: |nor_conv_3x3~0|+|skip_connect~0|nor_conv_1x1~1|+|none~0|nor_conv_3x3~1|avg_pool_3x3~2|

    Architectures already evaluated, with their measured accuracy:

    {history}

    Propose ONE new architecture that does not appear above and that you expect to score higher.

    Reply with the architecture string and nothing else. No explanation, no markdown, no code fences."""


def main():
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    api = create(None, 'tss', verbose=False, fast_mode=True)

    run_id = f"{datetime.now().strftime('%Y%m%dT%H%M%S')}-s{SEED}"
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    def log(**fields):
        row = {
            "run_id": run_id,
            "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "seed": SEED,
            "model": MODEL,
            "temperature": TEMPERATURE,
            **fields,
        }
        with LOG_PATH.open("a") as f:
            f.write(json.dumps(row) + "\n")

    def accuracy_of(arch):
        arch_str = arch.to_arch_str()
        idx = api.query_index_by_arch(arch_str)
        assert idx>=0, "Correct String format"
        acc = api.get_more_info(idx, 'cifar10', hp='200', is_random=False)['test-accuracy']
        api.clear_params(idx)
        return acc, idx


    random.seed(SEED)
    arch_list = deque([])
    for n in range(5):
        arch = random_arch(N_NODES)
        acc, idx = accuracy_of(arch)
        arch_list.append((arch, acc))
        log(phase="seed", iteration=-1, arch_str=arch.to_arch_str(),
            idx=idx, accuracy=acc, parse_ok=True)

    prompt = build_prompt(arch_list)

    for i in range(5):
        print(prompt)
        text = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=TEMPERATURE),).text

        result_arch = parse_response(text)
        if result_arch is None:
            print(f"iter {i}: PARSE FAIL <- {text[:90]!r}")
            log(phase="search", iteration=i, raw_response=text,
                arch_str=None, idx=None, accuracy=None, parse_ok=False)
            continue

        accuracy, idx = accuracy_of(result_arch)
        print(text, idx, accuracy)
        log(phase="search", iteration=i, raw_response=text,
            arch_str=result_arch.to_arch_str(), idx=idx,
            accuracy=accuracy, parse_ok=True)

        arch_list.append((result_arch, accuracy))
        #arch_list.popleft()
        prompt  = build_prompt(arch_list)


if __name__=="__main__":
    main()
