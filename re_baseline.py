from nats_bench import create
from search_space import random_arch, ArchConfig, OPS
from importlib.metadata import version
import random, statistics, os
from collections import deque

N_NODES = 4
SEED = 0
BUDGET = 100
POP= 20
SAMPLE = 5


def mutate(arch_str):
    arch = ArchConfig.from_arch_str(arch_str)
    edge = random.choice(arch.edges)
    edge[2] = random.choice([op for op in OPS if op != edge[2]])
    return arch.to_arch_str()

def query(api, arch_str):
    idx = api.query_index_by_arch(arch_str)
    assert idx>=0, "Correct String format"
    info = api.get_more_info(idx, 'cifar10', hp='200', is_random=False)
    api.clear_params(idx)
    return idx, info['test-accuracy']

def main():
    random.seed(SEED)
    api = create(None, 'tss', verbose=False, fast_mode=True)
    nats_bench_version = version("nats_bench")
    history = []
    pop = deque()
    best = dict()
    for i in range(POP):
        while True:
            arch_str = random_arch(N_NODES).to_arch_str()
            idx, accuracy = query(api, arch_str)
            if idx not in history:
                break

        history.append(idx)
        pop.append((arch_str, accuracy))
        if not best or accuracy> best["accuracy"]:
            best = {"idx":idx, "accuracy":accuracy}

    for i in range(POP, BUDGET):
        while True:
            sample = random.sample(list(pop), SAMPLE)
            parent = max(sample, key = lambda x: x[1])

            child_arch = mutate(parent[0])
            idx, accuracy = query(api, child_arch)
            if idx not in history:
                break

        if not best or accuracy> best["accuracy"]:
            best = {"idx":idx, "accuracy":accuracy}
        history.append(idx)
        pop.append((child_arch, accuracy))
        pop.popleft()

    os.makedirs("results", exist_ok=True)
    with open("results/re_seed0.md", "w") as f:
        f.write(f"Regularised Evoluation with Seed {SEED}\n\n")
        f.write(f"- best accuracy : {best['accuracy']:.3f}, idx : {best['idx']}\n")
        f.write(f"- queries: {len(history)}, unique: {len(set(history))}\n")
        f.write("- setting: CIFAR-10, hp='200', is_random=False, POP=20, SAMPLE=5\n")
        f.write(f"- vs random mean of maxima 93.832 +/- 0.183: {(best['accuracy']-93.832)/0.183:+.2f} sd\n")

    print("Best:", best)
    print("queries:", len(history), "unique:", len(set(history)))
    assert len(history) == BUDGET


if __name__=="__main__":
    main()
