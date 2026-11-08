from nats_bench import create
from search_space import random_arch
from importlib.metadata import version
import random, statistics, os
from bench import lookup


N_NODES = 4


def multi_seed_baseline(api, SEED):
    random.seed(SEED)
    valid_accuracies = []
    test_accuracies = []
    sampled_indices = []
    for i in range(100):
        arch = random_arch(N_NODES)
        arch_str = arch.to_arch_str()
        idx = api.query_index_by_arch(arch_str)

        assert idx>=0, "Correct String format"
        valid, test = lookup(api, idx)
        test_accuracies.append(test)
        valid_accuracies.append(valid)
        sampled_indices.append(idx)

    best_idx = max(range(len(valid_accuracies)), key = lambda l: valid_accuracies[l])
    valid_best_test = test_accuracies[best_idx]
    mean = statistics.mean(test_accuracies)
    minimum = min(test_accuracies)
    maximum = max(test_accuracies)
    stdev = statistics.stdev(test_accuracies)
    print(f"SEED: {SEED}")
    print("Here are the evaluation metrics:")
    print(f'Valid-selected Test: {valid_best_test}')
    print(f"MEAN: {mean:.3f}")
    print(f"MIN: {minimum:.3f}")
    print(f"MAX: {maximum:.3f}")
    print(f"STANDARD DEVIATION: {stdev:.3f}\n")

    return {
        "seed": SEED,
        "mean": mean,
        "minimum": minimum,
        "maximum": maximum,
        "stdev": stdev,
        "valid_best_test": valid_best_test,
        "sampled_indices": sampled_indices
    }


SEEDS = [42, 0, 1, 2, 3, 4, 5, 6, 7, 8]
SINGLE_SEED_MAX = 93.770   # results/random_baseline.md, seed 42, 6 Sep 2026
GLOBAL_OPTIMUM = 94.37     # verified best CIFAR-10 test accuracy in the TSS space


def reading(mean_vbt, std_vbt):
    """The paragraph this session exists to produce, written from measured numbers.

    Distances are expressed in standard deviations of the per-seed maximum.
    This is a description of spread, not a hypothesis test -- ten seeds is a
    small sample and the text says so.
    """
    z_single = (SINGLE_SEED_MAX - mean_vbt) / std_vbt
    z_gap = (GLOBAL_OPTIMUM - mean_vbt) / std_vbt

    out = []
    out.append(
        f"A 100-draw random search returns a maximum of "
        f"**{mean_vbt:.3f} ± {std_vbt:.3f}** across {len(SEEDS)} seeds. "
        f"The single-seed figure this project has been quoting, {SINGLE_SEED_MAX:.3f}, "
        f"sits {abs(z_single):.2f} standard deviations "
        f"{'above' if z_single > 0 else 'below'} that mean.\n\n"
    )

    if abs(z_single) <= 1.0:
        out.append(
            f"**So {SINGLE_SEED_MAX:.3f} is an ordinary draw, not a bar.** It is one "
            f"order statistic from one seed, it lands inside the normal spread of the "
            f"same procedure repeated, and beating it demonstrates nothing. The "
            f"comparison this paper has to make instead is against "
            f"{mean_vbt:.3f} ± {std_vbt:.3f}: a search result is only "
            f"interesting once it clears roughly "
            f"{mean_vbt + std_vbt:.3f}.\n\n"
        )
    else:
        out.append(
            f"**{SINGLE_SEED_MAX:.3f} was an unusually {'lucky' if z_single > 0 else 'poor'} "
            f"draw**, more than one standard deviation from the mean of repeated runs, "
            f"so it should not be carried forward as the baseline. Use "
            f"{mean_vbt:.3f} ± {std_vbt:.3f} in its place.\n\n"
        )

    out.append(
        f"Against the verified global optimum of {GLOBAL_OPTIMUM:.2f}, the headroom "
        f"from the random-search mean is {GLOBAL_OPTIMUM - mean_vbt:.3f} "
        f"accuracy points, or {z_gap:.2f} standard deviations. "
    )

    if z_gap >= 2.0:
        out.append(
            "**That gap survives the error bars.** Random search reliably stops short "
            "of the optimum by more than the run-to-run noise, so there is a real "
            "margin for a guided method to claim, and a result inside that margin "
            "would not be explainable as a lucky seed.\n"
        )
    elif z_gap >= 1.0:
        out.append(
            "**The gap is real but narrow** -- between one and two standard deviations. "
            "Any claimed improvement will need multiple seeds and a reported standard "
            "deviation to be credible at all, and a single good run will not be "
            "distinguishable from noise.\n"
        )
    else:
        out.append(
            "**The gap does not survive the error bars.** Run-to-run variation in "
            "random search is as large as the distance to the optimum itself, which "
            "means final accuracy cannot be this paper's headline metric -- the "
            "measurement is not sensitive enough to support it. Search efficiency "
            "(draws to reach a given accuracy) is the quantity with room left in it.\n"
        )

    out.append(
        f"\nCaveat stated rather than buried: {len(SEEDS)} seeds is a small sample and "
        f"these are distances in standard deviations, not a significance test. "
        f"The per-seed table above is the primary evidence.\n"
    )
    return "".join(out)


def main():
    api = create(None, 'tss', verbose=False, fast_mode=True)
    nats_bench_version = version("nats_bench")

    rows = []
    for seed in SEEDS:
        rows.append(multi_seed_baseline(api, seed))

    means = [r["mean"] for r in rows]
    maximas = [r["maximum"] for r in rows]
    mean_of_means = statistics.mean(means)
    stdev_of_means = statistics.stdev(means)
    mean_of_maximas = statistics.mean(maximas)
    stdev_of_maximas = statistics.stdev(maximas)
    vbt = [r['valid_best_test'] for r in rows]
    mean_vbt = statistics.mean(vbt)
    std_vbt = statistics.stdev(vbt)

    os.makedirs("results", exist_ok=True)
    with open("results/multi_seed_baseline.md", "w") as f:
        f.write("# Random Baseline, multi-seed (NATS-Bench-TSS, CIFAR-10)\n\n")
        f.write(f"- Seeds: {', '.join(str(s) for s in SEEDS)}\n")
        f.write(f"- nats_bench version: {nats_bench_version}\n")
        f.write("- Sample size: 100 random architectures per seed\n")
        f.write("- Setting: hp='200', is_random=False (averaged over all trials)\n\n")
        f.write("| Statistic | Value |\n")
        f.write("|-----------|-------|\n")
        f.write(f"| Mean of per-seed means | {mean_of_means:.3f} ± {stdev_of_means:.3f} |\n")
        f.write(f"| **Test acc of valid-selected arch (headline)** | **{mean_vbt:.3f} ± {std_vbt:.3f}** |\n")
        f.write(f"| Max test acc per seed (oracle, test-selected; NOT a fair baseline) | {mean_of_maximas:.3f} ± {stdev_of_maximas:.3f} |\n\n")
        f.write("## Per seed\n\n")
        f.write("| Seed | Mean | Max | Min | Std within seed |Valid-selected test |\n")
        f.write("|------|------|-----|-----|-----------------|----|\n")
        for r in rows:
            f.write(f"| {r['seed']} | {r['mean']:.3f} | {r['maximum']:.3f} | "
                    f"{r['minimum']:.3f} | {r['stdev']:.3f} |{r['valid_best_test']:.3f} \n")
        f.write("\n## Sampled architecture indices\n\n")
        for r in rows:
            f.write(f"**Seed {r['seed']}:** "
                    + ", ".join(str(idx) for idx in r["sampled_indices"]) + "\n\n")
        f.write("## Reading\n\n")
        f.write(reading(mean_of_maximas, stdev_of_maximas))

    print(f"Mean_of_means: {mean_of_means}")
    print(f"Stdev_of_means: {stdev_of_means}")
    print(f"Mean_of_maximas: {mean_of_maximas}")
    print(f"stdev_of_maximas: {stdev_of_maximas}")

if __name__=="__main__":
    main()