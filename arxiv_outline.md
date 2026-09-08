# Do LLMs Actually Search?

**Working title:** Do LLMs Actually Search? Random Search Is a Missing Baseline in LLM-Guided Neural Architecture Search

*Alternatives to test on readers before submission:*
- *"LLM-Guided NAS Has Never Been Compared to Random Search"*
- *"When Does an LLM Beat Random Search? A Controlled Study on NAS-Bench-201"*

**Author:** Adarsh Tiwari
**Status:** outline v3 · started 16 Aug 2026 · **rebuilt 20 Aug 2026 after reading LLMO, Feedback Memory, Convergence Theory and GraphIR**
**Venue plan:** arXiv preprint (cs.LG, cs.NE) 8 Nov 2026 → ICML 2027 ~28 Jan

---

## ★ THE STRATEGIC DECISION, RECORDED — read this before changing anything

**This is no longer a method paper. It is an audit plus a controlled study, and that change is the single highest-leverage decision in the project.**

A method paper from an unknown solo author competes on novelty against funded labs and loses. An audit competes on a question nobody has asked, and the answer is interesting whichever way it lands. The genre has a famous precedent: **Yu et al., "Evaluating the search phase of neural architecture search," ICLR 2020**, which showed classical NAS search phases were no better than random sampling. It is cited *inside* the Feedback Memory paper. **This is that paper for the LLM era.**

**Three things give this scope. Nothing else should be added.**

1. The question is binary, falsifiable, and unasked.
2. Both answers are publishable — a positive result maps the regime, a negative result corrects four recent papers.
3. It runs on table lookups. Zero GPU, one person, three months.

**Scope creep is the failure mode here, not scope shortage.** Every addition below has been checked against: does this make the headline claim stronger, or just longer?

---

## The headline claim — one sentence, one number

> *Fill this in the moment Table 2 exists. Everything else in the paper serves this sentence, and if it cannot be written in one line the paper is not finished.*

**"Across N budgets, M LLMs and 30 seeds on NAS-Bench-201, LLM-guided search beats random search by ____ and only below ____ evaluations."**

---

## Abstract — draft, ~150 words

> *Rewrite once Table 2 has real numbers. Do not polish before then.*

Large language models are increasingly proposed as search policies for neural
architecture search, and recent work reports consistent gains over prior iterations
or single-shot generation. We observe that across this literature, **random search is
never used as a baseline** — despite being the standard control in the NAS
literature since 2020, and despite costing nothing on tabular benchmarks. We audit
recent LLM-guided NAS work and find no study on NAS-Bench-201 that reports a
random-search comparison at a matched query budget. We then run that comparison:
LLM-guided search against random search, greedy search and regularized evolution,
across five query budgets, three LLMs and 30 seeds, with significance testing. We
find [RESULT]. We release a reproducible harness and all search logs. Our results
suggest that reported gains in this subfield are [CLAIM], and that budget-resolved
reporting against a random control should be standard practice.

---

## Five contributions — ordered by how much attention each earns

1. **An audit of the LLM-NAS literature against a single criterion: is random search
   a baseline?** A table of recent LLM-guided NAS papers scored on search space,
   comparator set, budget matching, seed count and significance testing. **This table
   is the reason the paper exists, it is quotable on its own, and it is the thing that
   gets screenshotted.** Current count: four papers read, zero with a random-search
   comparator.

2. **A direct reproduction of LLMO with the missing baseline added.** LLMO
   (Zhong et al., DOCS 2024) is the closest prior work, runs on our exact search
   space, and **publishes its source code** at
   `github.com/RuiZhong961230/LLMO`. We reproduce its protocol — same space, same
   30 trial runs, same fitness-evaluation budgets — and add random search plus
   variance and significance reporting, neither of which appears in the original.
   **Reproduction plus a missing control is a high-credibility, low-cost format and
   it makes the comparison unarguable.**

3. **Budget-resolved results rather than a single endpoint.** Prior work reports
   final accuracy at one budget. We report performance as a function of query budget
   across ~10 to ~1000 evaluations. **The low-budget regime is where any real
   difference must live**, because at 3000 evaluations on a 6,466-architecture
   non-isomorphic space every method is sampling half the space and the comparison is
   saturated. This is the observation that explains why all seven methods in LLMO's
   Table III fall within 0.30 percentage points.

4. **A history ablation that settles an open design question.** LLMO passes the
   LLM only the current best solution and its accuracy — **zero history**. Feedback
   Memory (arXiv:2603.12091) asserts K=5 in open code space **without ablating it**.
   Nobody has measured how much performance history actually helps in a fixed,
   enumerable space. We ablate 0/5/10/20 and answer it.

5. **An open evaluation harness and complete search logs.** Every run, every seed,
   every prompt, every returned architecture, released. **The harness is the artifact
   that outlives the paper and gets cited by people who never read it.** Name it,
   document it, give it a README a stranger can run in five minutes.

---

## The audit table — build this first, it is the paper's spine

Score every paper on the same five criteria. **Fill only from papers read in full.**

| Paper | Venue / date | Search space | Comparators | Random-search baseline | Matched budget | Seeds | Significance test |
|---|---|---|---|---|---|---|---|
| **LLMO** (Zhong et al.) | DOCS 2024 · arXiv:2406.05433 | NAS-Bench-201 cell | GA, PSO, DE, CMA-ES, JADE, SHADE | **✗** | ✓ (FE fixed) | 30 | **✗ — means only, no std** |
| **Feedback Memory** (Gu et al.) | arXiv:2603.12091 · Mar 2026 | Open code space | Single-shot generation only | **✗** | ✗ | **1** (seed 43) | ✗ |
| **Convergence Theory** (Adhikari et al.) | arXiv:2605.30103 · May 2026 | Open code space | None — no comparator | **✗** | ✗ | N = 12–16 | ✓ (Bonferroni) |
| **GraphIR** (Liu et al.) | arXiv:2608.01633 · Aug 2026 | Open code space | CPG / CodeRAG / GraphCode representations | **✗** | ✓ (100 iters) | 3–10 | ✗ (mean ± std only) |
| GENIUS | *to read* | | | | | | |
| EvoPrompting | *to read* | | | | | | |
| **Ours** | — | NAS-Bench-201 cell | **Random**, greedy, GA, regularized evolution | **✓** | ✓ | **30** | ✓ |

**The observation this table produces, stated plainly:** four papers, four different
research groups, zero random-search baselines. Two report no variance at all. One
runs a single seed. **The subfield has been measuring improvement against itself.**

---

## Experimental design — locked, and deliberately small

| Dimension | Setting | Why |
|---|---|---|
| Search space | NAS-Bench-201 topology (15,625 archs, 6,466 non-isomorphic) | Exhaustive ground truth. Zero GPU. Same space as LLMO — direct comparability. |
| Datasets | CIFAR-10, CIFAR-100, ImageNet16-120 | All three ship with the benchmark. Third dataset is free and widens the claim. |
| Objective | Clean validation accuracy | LLMO optimises adversarial robustness. Ours is the standard objective, which makes the result about search rather than about attacks. |
| Query budgets | 10, 25, 50, 100, 250, 500, 1000 | The curve is the contribution. Saturation above ~1000 is expected and should be shown, not hidden. |
| Seeds | **30** | Matches LLMO exactly. Free on lookups. Removes the obvious reviewer objection. |
| LLMs | Gemini (free tier) + 2 free-tier alternatives | LLMO used one model. Three makes the finding about *LLMs*, not about Gemini. **Only if the free quota allows — this is the first thing cut.** |
| Baselines | **Random search**, greedy hill-climb, GA, regularized evolution | Random is the point. Regularized evolution is the standard strong NAS baseline. |
| Statistics | Mean ± std, Wilcoxon signed-rank, bootstrap CIs on the budget curve | The gap in every paper in the audit table. |

**Justification for the tabular benchmark, and it is a strength not an apology:**
an open code space has no ground truth, so every candidate must be trained, which
makes an equal-cost random-search baseline prohibitively expensive — plausibly why
nobody has run one. Theorem 8 of arXiv:2605.30103 gives σ²_arch ≫ σ²_noise as the
condition for trustworthy proxy rankings and notes zero-shot proxies on
NAS-Bench-101/201 explain at most R² ≈ 0.67. **A table lookup has σ²_noise ≈ 0.**
Their own framework says this is the right place to run the experiment.

---

## If the result is a tie — the contingency, decided in advance

**Do not treat a null as a failure and do not bury it.** If LLM-guided search does
not beat random search at any budget, the paper gets *stronger* and the framing
shifts one step outward:

> At the scale of the benchmark this subfield uses, LLM guidance provides no
> measurable advantage over random sampling. Reported gains are consistent with
> search-space saturation rather than with model capability.

That is a methodological correction to four papers, it follows Yu et al. (ICLR 2020)
exactly, and it is more citable than a 0.2% win. **Deciding this now means the result
cannot be talked into looking positive later.**

---

## What is deliberately NOT in this paper

Recorded so it stays out.

- ❌ A new search method or prompting mechanism. Feedback Memory owns structured
  history; we cite it and move on.
- ❌ Open code space. It makes the controlled comparison impossible, which is the
  whole point.
- ❌ Adversarial robustness. LLMO's objective, not ours.
- ❌ A second search space. Reconsider only at ICML revision time, never before arXiv.
- ❌ Fine-tuning any model. Frozen, prompted, zero cost.

---

## Timeline against the existing plan

| Date | Milestone |
|---|---|
| Thu 27 Aug | `nas_bench_lookup` verified · **random-search baseline number over 100 archs — the paper's first real number** |
| Tue 1 Sep | Related Work draft, 400 words · audit table populated |
| Thu 3 Sep | Serializer implemented, three formats |
| **Sun 6 Sep** | **Phase 0 close-out — repo, baseline number, serializer working** |
| Sep–Oct | LLMO reproduction · budget sweep · history ablation |
| **Sun 8 Nov** | **arXiv submission** |
| ~28 Jan 2027 | ICML 2027 (verify date by search first) |

---

## Reading log

| Paper | Read | The one thing that matters |
|---|---|---|
| **LLMO** · arXiv:2406.05433 | ✅ 20 Aug | Hill-climber with Gemini as mutation operator — **passes only the current best, zero history**. Six MHA baselines, **no random search**, 30 runs but **no std and no significance test**. All seven methods within 0.30pp. Code public. |
| **Feedback Memory** · 2603.12091 | ✅ 20 Aug | K=5 diagnostic triples in open code space. Baseline is single-shot only, **one seed**. Owns "structured history" — cite, do not claim. |
| **Convergence Theory** · 2605.30103 | ✅ 20 Aug | Proves the process improves against itself; **no comparator anywhere**. Theorem 8 justifies our benchmark choice. Asks for third-party replication. |
| **GraphIR** · 2608.01633 | ✅ 20 Aug | Representation paper, different benchmarks, no collision. Sets the multi-seed bar at 3–10. |
| GENIUS | ☐ | Its serialisation design — the decision to copy or beat. *(carried from 18 Aug)* |
| EvoPrompting | ☐ | Performance history or code only? Note: needs soft prompt-tuning; we do not. |
| Yu et al., ICLR 2020 | ☐ *optional* | *"Evaluating the search phase of NAS."* The genre precedent. **Not a prerequisite for anything. Use as shadowing material or skip.** |

> ### ⛔ READING IS CLOSED FOR PHASE 0 — 20 Aug 2026
>
> **Four papers were read on 20 Aug and they resolved the novelty question. That question is answered and does not get reopened.**
>
> The remaining rows are optional and none of them blocks a single line of code. **The next paper sessions build, they do not read:** benchmark setup on Tue 25 Aug, random-search baseline on Thu 27 Aug. Related Work on 1 Sep is written from the four papers already read.
>
> **Any new paper added to this list must displace one, not extend the list.** Three times on 20 Aug a completed reading task was followed by a new one; that is how a queue grows faster than it is cleared, and it is a planning defect rather than a knowledge gap.

---

## Distribution — the paper does not distribute itself

*Recorded here because the Medium post shipped and did not travel, and the cause was
distribution, not quality.*

- The **audit table** is the shareable object, not the abstract. One image, one
  sentence: *"Four recent LLM-NAS papers. Zero random-search baselines."*
- Post the finding **when the audit table is done**, before the results exist. The
  audit is interesting on its own and it builds an audience for the result.
- Send the preprint directly to the three authors whose work is audited. Ignatov and
  Timofte are on three of the four papers. **A courteous, specific note to someone
  whose paper you engaged seriously is the single highest-yield message in this
  project** — far higher than a cold note to a stranger.
- The harness README is a distribution channel. Someone who runs your code cites you.

---

## Field note — who reviews this

**Dmitry Ignatov and Radu Timofte** are authors on three of the four papers audited
and on seven of the 107 results in the scan. They run a sustained programme on this
at Würzburg and are likely reviewers.

**Engage their work generously and precisely.** The argument is not that their methods
fail — it is that the field has not yet run the equal-cost control, and a tabular
benchmark is where it can be run for free. That framing is both the honest one and
the one that survives review.