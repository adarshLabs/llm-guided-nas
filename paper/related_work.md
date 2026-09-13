# Related Work

## Evaluation on NAS-Bench-201: a note on what accuracy means here
All experiments use NAS-Bench-201, a tabular benchmark of 15,625 architectures.
An exhaustive enumeration of the full space (`hp=200`, `is_random=False`) gives a
best CIFAR-10 test accuracy of **94.37%**, at architecture 6111. One hundred
architectures sampled uniformly at random (seed 42) give:

| Mean | Max | Min | Std |
|------|-----|-----|-----|
| 88.303 | 93.770 | 68.073 | 5.634 |

That is within 0.60 points of the global optimum of the entire space, with no
search of any kind. Looking at individual samples makes the issue clear: when
`none` edges remove intermediate nodes, some architectures collapse to a single
1×1 convolution while still achieving 88.60% accuracy. Final accuracy on this
benchmark therefore carries almost no information — a headline figure in the low
94s must be read against a random 93.77%. This work instead fixes a target
accuracy and reports the number of queries required to reach it.

## LLM-guided program and architecture search
The three systems follow a similar pattern: the language model acts as a proposal mechanism within a search loop rather than being the object of optimization itself. It generates candidates, which are then evaluated externally. The main differences lie in the search space and evaluation setting: open-ended programs, open architecture spaces, and a tabular benchmark, respectively.

### FunSearch (Romera-Paredes et al., Nature 625:468–475, 2024)
FunSearch combines a pretrained LLM with a systematic evaluator to search over programs, and applies this approach to open problems in combinatorics such as the cap set problem and online bin packing. The LLM proposes changes to a seed program, the evaluator scores each candidate, and high-scoring programs are fed back into subsequent prompts. This feedback loop grounds the LLM's generation in measured performance rather than relying on the model's own assessment, and the authors report solutions that improve on previously known human-designed results. FunSearch operates in an open-ended program space where each candidate must be executed and evaluated, whereas we search a closed, fully enumerated space with a known result for every query; this makes query count a direct measure of search efficiency and the main quantity we report.

### EvoPrompting (Chen, Dohan and So, NeurIPS 2023)
EvoPrompting uses language models as adaptive mutation and crossover operators within an evolutionary neural architecture search loop. It combines evolutionary prompt engineering with soft prompt tuning on successful candidates, and the authors show that naive few-shot prompting performs poorly on this task. They report convolutional architectures on MNIST-1D that outperform both human-designed baselines and naive few-shot prompting in accuracy and model size, as well as graph neural networks that outperform the state of the art on 21 of 30 CLRS algorithmic reasoning tasks at comparable model sizes. EvoPrompting shows that an LLM can effectively serve as an evolutionary operator, but it evaluates open search spaces where query efficiency is not directly measured; in contrast, we use a tabular benchmark and report queries-to-target against a random baseline under the same search space and seed, allowing the LLM's contribution to be measured per query.

### GENIUS (Zheng et al., arXiv:2304.10970, 2023)
GENIUS uses GPT-4 as a black-box optimizer for neural architecture search and is the closest prior work to ours in terms of setting. GPT-4 is given the search space, proposes candidate architectures, receives their measured performance, and uses this feedback to refine subsequent proposals. The authors explicitly state that their goal is not to achieve state-of-the-art performance, but to show that a simple prompting approach with limited domain expertise can effectively navigate the search space. We build on this setting but focus on search efficiency: since uniform random sampling reaches 93.77% on NAS-Bench-201 within 100 queries, final accuracy alone is not enough to distinguish methods, so we report queries-to-target and also study the serialization format as a controlled variable.

## Classical NAS baselines
Regularized Evolution (Real et al., 2019) is a standard NAS baseline that uses aging tournament selection to iteratively evolve architectures. DARTS (Liu et al., 2019) takes a different approach by relaxing the discrete search space into a continuous one and optimizing architecture choices with gradients. Both are commonly evaluated using GPU-hours and final accuracy. On a tabular benchmark, GPU-hours are not the binding cost. We therefore report queries-to-target, putting LLM-based, evolutionary, and random search on the same axis.