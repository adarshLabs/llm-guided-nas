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

**Answer:**

**If yes:** the "structured performance history rather than code generation" framing is not new. Cite it and reposition.

---

### 2. Convergence Theory for Iterative LLM-Based NAS
https://arxiv.org/abs/2605.30103

**Question:** Does it state the conditions under which iterative LLM search beats random search?

**Answer:**

**If yes:** the "characterise the regime where it fails" claim has a prior. An *empirical, budget-matched* regime characterisation may still stand — but it is a complement to this, not a discovery.

---

### 3. GraphIR: Architecture-Level Search States
https://arxiv.org/abs/2608.01633

**Question:** Does it evaluate on NAS-Bench-201 / NATS-Bench topology space?

**Answer:**

**If yes:** you are on a shared benchmark with a paper 18 days old. "First" is gone.

---

## FIELD NOTE

**Dmitry Ignatov and Radu Timofte appear as authors on seven of the 107 results** (2608.00078, 2607.11591, 2605.30103, 2605.04903, 2603.12091, 2601.08517, 2601.02997, plus NNGPT 2511.20333). They are running a sustained programme on exactly this problem and are among the most likely reviewers of this submission. Their line of work should be engaged directly in Related Work, not cited in passing.

---

## SURVIVING CONTRIBUTION

> Rewrite after answering the three questions above. If all three come back "yes," this is the floor, and it is still publishable:

**A budget-matched, multi-seed controlled comparison of LLM-guided search against random and evolutionary baselines on NAS-Bench-201, reporting the regime in which the LLM-guided method loses.**

Rigour and a clean negative result are the contribution. Novelty of mechanism is not.