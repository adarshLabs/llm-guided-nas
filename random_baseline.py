from nats_bench import create
from search_space import random_arch
from importlib.metadata import version
import random, statistics, os

N_NODES = 4
SEED = 42

def main():
    random.seed(SEED)
    api = create(None, 'tss', verbose=False, fast_mode=True)
    nats_bench_version = version("nats_bench")
    test_accuracies = []
    sampled_indices = []
    for i in range(100):
        arch = random_arch(N_NODES)
        arch_str = arch.to_arch_str()
        idx = api.query_index_by_arch(arch_str)

        assert idx>=0, "Correct String format"
        info = api.get_more_info(idx, 'cifar10', hp='200', is_random=False)
        print(f"{i}th run {idx} test accuracy: {info['test-accuracy']}")
        test_accuracies.append(info['test-accuracy'])
        sampled_indices.append(idx)
        api.clear_params(idx)

    mean = statistics.mean(test_accuracies)
    minimum = min(test_accuracies)
    maximum = max(test_accuracies)
    stdev = statistics.stdev(test_accuracies)

    print("Here are the evaluation metrics:")
    print(f"MEAN: {mean:.3f}")
    print(f"MIN: {minimum:.3f}")
    print(f"MAX: {maximum:.3f}")
    print(f"STANDARD DEVIATION: {stdev:.3f}")

    os.makedirs("results", exist_ok=True)
    with open("results/random_baseline.md", "w") as f:
        f.write("# Random Baseline (NATS-Bench-TSS, CIFAR-10)\n\n")
        f.write(f"- Seed: {SEED}\n")
        f.write(f"- nats_bench version: {nats_bench_version}\n")
        f.write("- Sample size: 100 random architectures\n")
        f.write("- Setting: hp='200', is_random=False (averaged over all trials)\n\n")
        f.write(f"| Mean | Max | Min | Std |\n")
        f.write(f"|------|-----|-----|-----|\n")
        f.write(f"| {mean:.3f} | {maximum:.3f} | {minimum:.3f} | {stdev:.3f} |\n\n")
        f.write("## Sampled architecture indices\n\n")
        f.write(", ".join(str(idx) for idx in sampled_indices) + "\n")


if __name__=="__main__":
    main()