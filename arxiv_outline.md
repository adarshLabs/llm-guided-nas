# LLM-Guided Neural Architecture Search

**Working title:** When Does an LLM Beat Random Search? A Controlled Study of LLM-Guided Neural Architecture Search on NAS-Bench-201

**Author:** Adarsh Tiwari
**Status:** draft outline · started 16 Aug 2026 · arXiv target 8 Nov 2026
**Venue plan:** arXiv preprint (cs.LG, cs.NE) → ICML 2027

---

## Abstract — draft, ~150 words

> *This is a first draft to edit, not a final one. Rewrite it once Table 1 has real numbers.*

Large language models have been proposed as search policies for neural architecture
search, but existing work reports wins without controlling for query budget or
reporting variance across seeds, which makes it unclear whether the gains come from
the model or from the search budget. We evaluate an LLM as a search policy on
NAS-Bench-201, giving the model structured performance history over previously
evaluated architectures rather than asking it to generate code. We compare against
random search, greedy search and regularized evolution at matched query budgets
across five seeds. We find that LLM-guided search outperforms random search in the
low-budget regime, where its advantage comes from exploiting history, and that this
advantage narrows as the budget grows. We characterise both regimes, ablate history
length and architecture serialisation format, and release a pipeline that runs
without GPU compute for the search phase.

---

## The contribution — do not drift from this

We evaluate an LLM as a search policy for neural architecture search, using
structured performance history rather than code generation, and provide the first
controlled comparison against random and evolutionary baselines on NAS-Bench-201
with matched query budgets and multi-seed statistics. We characterise the regime in
which LLM-guided search outperforms random search, and the regime in which it does
not.

**The second sentence is the paper.** Everyone claims their method wins. Almost
nobody publishes a clean statement of when it loses.

---

## Five claimed contributions

1. **A controlled comparison at matched query budgets.** The first evaluation of an
   LLM search policy against random search, greedy search and regularized evolution
   on NAS-Bench-201 with identical query budgets and multi-seed statistics.

2. **A structured-history prompting formulation.** The LLM receives a serialised
   table of previously evaluated architectures and their accuracies, and proposes the
   next architecture directly — no code generation, no gradient signal.

3. **A characterisation of the failure regime.** We identify the budget and search
   space conditions under which LLM-guided search fails to beat random search, and
   report them as a primary result rather than an appendix.

4. **Ablations over the design choices that actually matter.** History length
   (0/5/10/20), architecture serialisation format (adjacency list vs. performance
   table vs. combined), and model size.

5. **A reproducible zero-GPU search pipeline.** The search phase uses NAS-Bench-201
   lookups and a free-tier LLM API, so the full study reproduces without GPU compute.
   One real training run validates the best found architecture.

---

## Open questions to resolve before Phase 1

- [ ] Which serialisation format goes in v1? The other two become Ablation 2. *(Thu 3 Sep)*
- [ ] Has anything published since Jul 2026 killed the novelty claim? *(Thu 20 Aug)*
- [ ] What is the random-search baseline number over 100 architectures? *(Thu 27 Aug)*

---

## Reading log

| Paper | Read | The one thing that matters |
|---|---|---|
| FunSearch (DeepMind, 2023) | ☐ | How does the proposal loop feed results back to the model? |
| EvoPrompting | ☐ | Does it give the model performance history, or only code? |
| GENIUS | ☐ | Its architecture serialisation — the decision I copy or beat *(Tue 18 Aug)* |

**100 words on what is genuinely different between FunSearch and EvoPrompting:**

*(Till to write here)*
