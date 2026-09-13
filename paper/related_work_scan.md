# Related Work Scan — LLM-Guided NAS

**Scanned:** 20 Aug 2026
**Query:** arXiv all-fields `LLM neural architecture search`, 107 results, sorted by announcement date (newest first)
**Filter:** kept only work where a language model *proposes or mutates* architectures. Excluded work that only uses a model to predict or rank accuracy.

---

## KEPT — 15 entries

### Directly on LLM-guided NAS

- **GraphIR: Architecture-Level Search States for LLM-Guided Neural Architecture Evolution** — https://arxiv.org/abs/2608.01633 · 2 Aug 2026
- **Device-First Feedback: Toward Mobile-Native LLM-Driven Neural Architecture Search** — https://arxiv.org/abs/2608.00078 · 29 Jul 2026
- **Agentic Neural Architecture Search** — https://arxiv.org/abs/2607.07984 · 8 Jul 2026
- **LLM-Driven AutoML for Cross-Lingual Handwritten OCR: Closed-Loop NAS with GPT-5, GPT-4o, Claude Sonnet 4** — https://arxiv.org/abs/2607.15509 · 16 Jul 2026 (ICCKE 2025)
- **Similarity-Guided Curriculum Fine-Tuning of LLMs for Neural Architecture Synthesis** — https://arxiv.org/abs/2607.11591 · 13 Jul 2026
- **Consensus-gated Multi-Agent Neural Architecture Search for Seismic Fault Segmentation** — https://arxiv.org/abs/2608.13889 · 13 Aug 2026
- **TacEvo: Self-Evolving Architecture Discovery for Robotic Tactile Perception via LLM-Driven Quality-Diversity Search** — https://arxiv.org/abs/2606.30109 · 29 Jun 2026
- **Convergence Theory for Iterative LLM-Based Neural Architecture Search: A Parametric Cross-Entropy Framework with Closed-Form Proxy Reliability** — https://arxiv.org/abs/2605.30103 · 28 May 2026 (submitted NeurIPS 2026)
- **Resource-Efficient Iterative LLM-Based NAS with Feedback Memory** — https://arxiv.org/abs/2603.12091 · 12 Mar 2026
- **Structured Progressive Knowledge Activation for LLM-Driven Neural Architecture Search** — https://arxiv.org/abs/2605.04057 · 10 Apr 2026

### Adjacent — LLM proposes designs, different domain or object

- **Improving Auto-Design of Neural PDE Solvers with a Domain-Specific Language** — https://arxiv.org/abs/2608.04384 · 4 Aug 2026
- **Evolutionary Algorithm-Guided LLMs for Physics-Informed Neural Network Design** — https://arxiv.org/abs/2607.15560 · 16 Jul 2026
- **EvoPINN: Agentic Discovery of Executable Algorithms for Physics-Informed Neural Networks** — https://arxiv.org/abs/2607.26490 · 29 Jul 2026
- **Large Discovery Models: Empirically-grounded Model-Based Open-Ended Search** — https://arxiv.org/abs/2608.15669 · 16 Aug 2026
- **GAE: Graph-Augmented Evolution for Scientific Discovery via Reinforcement Optimization** — https://arxiv.org/abs/2607.10127 · 11 Jul 2026 (ICML 2026 AI4Science Workshop)

---

## EXCLUDED, with reasons

| Paper | Why excluded |
|---|---|
| PRISM: Predictive Protocol for Permutation Optimization (2608.08344) | Fitness-landscape diagnostics select a search strategy. No language model proposing architectures. |
| Bi-NAS (2607.01387) | Bi-level NAS for recommender explanation. No language model in the search loop. |
| Spatially Fine-Grained DVFS in NPUs (2607.16473) | Serving-hardware energy efficiency. Not architecture search. |

---

## THE THREE CLOSEST — novelty check

> One sentence each. Answer the specific question. If the answer is yes, the corresponding contribution comes out of `arxiv_outline.md` — deleted, not softened.

### 1. Resource-Efficient Iterative LLM-Based NAS with Feedback Memory
https://arxiv.org/abs/2603.12091

**Question:** Does it feed the model a structured record of past architectures *and their accuracies*?

**Answer: Partially yes — read the full paper, not just the abstract.**

The feedback memory is a sliding window of **K=5 "structured diagnostic
triples"**: `(problem, suggestion, outcome)`, where `outcome` is the accuracy
achieved or the error encountered (Eq. 3). That is a structured performance
record, but it is not a plain `(architecture, accuracy)` pair — it carries
the LLM's own diagnosis and suggested fix, which our design does not.

Three things this settles:

- **The "structured history, not code generation" framing has a real prior
  here and needs citing, not claiming as new.** Reposition contribution 1/4
  around this rather than asserting novelty of the framing itself.
- **The K-sweep is still open.** The paper's only ablation (Fig. 3, §5)
  compares "with memory" vs. "without memory" — roughly K=5 vs. K=0. There is
  **no reported sweep across K=5/10/20.** Our planned ablation survives, but
  should be described as *the first K-sweep*, not *the first history
  ablation* — Feedback Memory already ran the binary version of that
  question.
- **No random-search baseline anywhere.** Confirmed directly: "We compare
  against single-shot generation... representing what the LLM produces from
  its pre-trained knowledge alone without any feedback signal." Single-shot
  is the only comparator in the paper.

**Correction to fold back into `arxiv_outline.md`'s audit table:** the
Significance-test column currently marks Feedback Memory **✗**. That's not
quite right — the paper *does* run significance tests, just not against a
baseline: it reports Spearman ρ and Kendall τ rank-correlation tests on the
accuracy-vs-iteration trend within its own method ("statistically significant
improvement over single-shot generation"). "No significance test against a
comparator" is accurate; "no significance test at all" is not. Fix the cell
to something like **✗ (trend test only, not vs. a baseline)**.

---

### 2. Convergence Theory for Iterative LLM-Based NAS
https://arxiv.org/abs/2605.30103

**Question:** Does it state the conditions under which iterative LLM search beats random search?

**Answer: No — read the full paper, not just the abstract.**

The theorems (monotonically non-decreasing expected architecture quality,
geometric convergence of the elite-set probability to a fixed point)
describe how the method behaves **relative to its own earlier iterations**.
None of them compares against random sampling — the closest theoretical
question posed is "does iterative LLM fine-tuning provably improve
architecture quality?", which is about self-improvement, not about beating a
random baseline.

The empirical section (Table 1/2, N∈{12,15,16} per LLM, Bonferroni-corrected
across the three LLMs, only Mistral survives correction) compares three LLMs
against each other and compares delta-generation vs. full-code generation.
**It has no random-search or any other search-strategy baseline**, and it
runs on an open code-generation space (the set of valid `torch.nn.Module`
programs, warm-started from the 626-architecture LEMUR dataset) — not
NAS-Bench-201.

**Verdict: the "characterise the regime where LLM-guided search loses to
random" claim is untouched.** This paper doesn't make that claim,
theoretically or empirically. Cite it for its convergence result and its
explicit call for third-party replication (a good hook — "we are the
replication") — not as a competing claim.

---

### 3. GraphIR: Architecture-Level Search States
https://arxiv.org/abs/2608.01633

**Question:** Does it evaluate on NAS-Bench-201 / NATS-Bench topology space?

**Answer: No — read the full paper, not just the abstract.**

GraphIR evaluates on **six benchmarks across five domains, all non-vision-NAS**:
CLRS (algorithmic reasoning), MNIST1D-Shuffle (1D sequence classification),
20 Newsgroups (text classification), CartPole-v1 (RL control), and two
tabular sets (Yeast, Breast Cancer Wisconsin). NAS-Bench-201/NATS-Bench does
not appear anywhere. Its comparators are EvoPrompting, OpenEvolve, Spark, and
alternative code-representation baselines (CPG-/CodeRAG-/GraphCode-style) —
not random search. Up to 10 seeds with mean±std on some benchmarks (matches
the outline's "3–10" note), no significance test.

**Verdict: "first on this shared benchmark" stands.** GraphIR is close in
spirit (LLM-guided architecture evolution, structured search state) and
18 days old, but it is on a disjoint set of benchmarks. Zero collision risk
with the NAS-Bench-201 study.

---

## FIELD NOTE

**Dmitry Ignatov and Radu Timofte appear as authors on seven of the 107 results** (2608.00078, 2607.11591, 2605.30103, 2605.04903, 2603.12091, 2601.08517, 2601.02997, plus NNGPT 2511.20333). They are running a sustained programme on exactly this problem and are among the most likely reviewers of this submission. Their line of work should be engaged directly in Related Work, not cited in passing.

---

## FOURTH CHECK — a paper the date-sorted scan missed

**GENIUS** (Zheng et al., "Can GPT-4 Perform Neural Architecture Search?",
arXiv:2304.10970, Aug 2023) is not in the KEPT list above because the scan
query was date-sorted from a 107-result pull and GENIUS predates that window
by three years — it was already on this project's separate reading list
(see `arxiv_outline.md`'s audit table and reading log), not caught by this
scan. It matters enough to note here: **read the full paper**, not the
abstract.

- **It evaluates on NAS-Bench-201 itself** — CIFAR-10, CIFAR-100 and
  ImageNet16-120, the exact benchmark and datasets this project uses — plus
  NAS-Bench-Macro, Channel-Bench-Macro and an ImageNet/MobileNetV2 space.
  This makes GENIUS the closest prior work by benchmark, closer than LLMO.
- **It does not use a random-search baseline on NAS-Bench-201.** Table 1
  reports GENIUS-only numbers (5 trials, 10-iteration budget: CIFAR-10
  93.79±0.09, CIFAR-100 70.91±0.72, ImageNet16-120 44.96±1.02 — for
  reference, the verified global optima are 94.37 / 73.51 / 47.31). So the
  audit's central claim survives GENIUS too.
- **But it does use random sampling as a baseline elsewhere in the same
  paper** — on NAS-Bench-Macro, where it reports "randomly sampled
  architectures are typically employed as a baseline" and runs 10,000
  repetitions of the 10-iteration process to get baseline variance. That is
  a stronger anecdote for the audit's motivation than "the field never
  thought of it": **the authors clearly know the convention and apply it on
  one benchmark, then don't carry it over to NAS-Bench-201** — the gap looks
  like an inconsistency, not an oversight born of ignorance, which is a
  sharper and more specific framing than the outline currently uses.
- Serialization: "encoding the NAS problem statement into a human-readable
  text format" plus, for ImageNet, a FLOPs lookup table in the prompt.
  Prompt carries **only the current best architecture and its accuracy**,
  no history — same zero-history design LLMO uses.

**Action:** add GENIUS as a row in `arxiv_outline.md`'s audit table (done —
see that file) and weigh it against LLMO as the reproduction target for
contribution 2 — GENIUS shares the identical benchmark and datasets, which
LLMO does not (LLMO optimises adversarial robustness, not clean accuracy).

---

## SURVIVING CONTRIBUTION

> All three closest 2026 papers came back **no** on the specific threat
> question, and the fourth check (GENIUS) also comes back no. The full
> contribution set in `arxiv_outline.md` survives, not just the fallback
> floor:

**A budget-matched, multi-seed controlled comparison of LLM-guided search
against random and evolutionary baselines on NAS-Bench-201, reporting the
regime in which the LLM-guided method loses.**

Rigour and a clean negative result are the contribution. Novelty of
mechanism is not. Two adjustments earned by this check: (1) contribution 4
is a **K-sweep**, not the first history ablation — Feedback Memory already
ran the K=0-vs-K=5 binary version; (2) GENIUS, not only LLMO, deserves a
reproduction slot, since it is the only prior work sharing the exact
benchmark and datasets.