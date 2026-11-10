import argparse, json, os
import random_baseline, re_baseline

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--method", choices=["random", "re"], required=True)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--budget", type=int, default=100)
    parser.add_argument("--dataset", choices=["cifar10"], default="cifar10")
    return parser.parse_args()

def main():
    args = parse_args()

    module = random_baseline if args.method=="random" else re_baseline
    out_dir = "results/runs"
    path = os.path.join(out_dir, f"{args.method}_seed{args.seed}.jsonl")
    records = module.main(seed=args.seed, budget=args.budget, write_files=False)
    os.makedirs(out_dir, exist_ok=True)
    with open(path, "w") as f:
        f.write(json.dumps({"method": args.method, "seed": args.seed}) + "\n")
        for query, (idx, valid, test) in enumerate(records):
            f.write(json.dumps({"query": query, "idx": idx, "valid": valid, "test": test}) + "\n")
    
    print("wrote", path)

if __name__=="__main__":
    main()