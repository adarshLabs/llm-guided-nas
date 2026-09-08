# Understanding Your Own Paper — LLM-Guided NAS

**Written 16 Aug 2026 · move this into `llm-guided-nas/paper/`**

This assumes you know NAS. You wrote a thesis on it. So this does not explain what a
search space is, what a supernet is, or why weight sharing is fragile — you already
argued all of that. It explains **the four things in this project that are genuinely
new to you**, and the reading that makes each one land.

---

## 1 · What is actually different from your M.Tech thesis

| | M.Tech thesis (2025) | This paper |
|---|---|---|
| **Question** | Which architecture is best for morph-attack detection? | Is an LLM a good *search policy*? |
| **Search strategy** | MIGO — information-geometric optimisation | An LLM proposing the next architecture |
| **Evaluation** | Real training, 132 GPU-hours, 6 datasets | Dictionary lookup. **Zero GPU for the search** |
| **Contribution type** | Applied — a method for a domain | Empirical — a controlled study of a method |
| **What a reviewer attacks** | Does it generalise across datasets? | Is it better than random, and did you prove it? |

**The single sentence:** your thesis asked *what architecture wins*. This paper asks
*whether an LLM is a good way to look for one* — and, unusually, is willing to publish
"sometimes no."

You are not switching fields. You are switching from being the person who applies a
search strategy to the person who evaluates one. That is the move from engineer to
scientist, and it is exactly the move Applied Scientist interviews probe.

---

## 2 · Prerequisite: the NAS-Bench-201 search space, concretely

Small enough to hold in your head, which is the point.

- A **cell** with **4 nodes**. Nodes are feature maps.
- Every node connects to every later node → **6 edges** (0→1, 0→2, 1→2, 0→3, 1→3, 2→3).
- Each edge carries **one of 5 operations**: `none`, `skip_connect`, `nor_conv_1x1`,
  `nor_conv_3x3`, `avg_pool_3x3`.
- So the space is **5⁶ = 15,625 architectures.** All of them. Exhaustively enumerated.

The string format you will parse looks like:

```
|nor_conv_3x3~0|+|nor_conv_3x3~0|none~1|+|nor_conv_1x1~0|nor_conv_3x3~1|nor_conv_3x3~2|
```

Read it as three groups separated by `+`: edges into node 1, then into node 2, then
into node 3. `op~i` means "operation `op` on the edge from node `i`."

**Why 15,625 matters:** it is small enough that every architecture has already been
trained, and large enough that a search still has to be clever. That combination is
what makes it a benchmark rather than a toy.

---

## 3 · Prerequisite: tabular benchmarks, and why you train nothing

This is the biggest conceptual shift from your thesis.

Someone trained all 15,625 architectures on CIFAR-10, CIFAR-100 and ImageNet16-120,
multiple seeds each, and published the results as a lookup table. Your "trainer" is:

```python
accuracy = api.get_more_info(arch_index, 'cifar10')
```

**Why the field built these.** Around 2019 NAS had a reproducibility problem: papers
reported wins that came from different training setups, different budgets and single
seeds, so nobody could tell whether a search strategy or a learning-rate schedule was
doing the work. Several papers showed that **random search with the same budget matched
most published methods.** Tabular benchmarks exist so that the search strategy is the
only variable.

**What it costs you.** You can only search inside this exact space, and results here do
not automatically transfer to a real design problem. Reviewers know this. You state it
as a limitation rather than waiting to be told.

**What it buys you.** A five-seed, four-method, matched-budget study on a laptop.
Without it, this paper needs a GPU cluster and does not exist.

---

## 4 · Prerequisite: query budget is the unit of comparison

A **query** = one architecture evaluated = one table lookup.

Every method gets the *same* number of queries — say 100 — and you compare the best
accuracy each one found. This sounds obvious and it is the single most common flaw in
the papers you are competing with: methods get compared at different budgets, so the
"better" method was often just the one allowed more guesses.

**Matched query budgets are your first contribution.** Not because it is clever, but
because it is the control that makes the comparison mean anything.

---

## 5 · Prerequisite: the three baselines, and why the third is non-negotiable

| Baseline | What it does | Why it is there |
|---|---|---|
| **Random search** | Sample uniformly, keep the best | The sanity check. Every reviewer asks. A method that does not beat random is not a method |
| **Greedy / local search** | Mutate the current best, keep improvements | Cheap, surprisingly strong, catches "the space is easy" |
| **Regularized evolution** | Tournament selection with an age-based population *(Real et al., 2019)* | **The standard strong baseline in NAS.** Its absence is the most likely desk-reject reason for this paper |

Your thesis compared DARTS, STGS, GRMC and MIGO. Those are search *methods for a
supernet*. These three are search *strategies over a discrete space* — different
family, same role.

---

## 6 · Prerequisite: LLM-as-optimizer, the actual related work

The area is about three years old and small. Four papers, in the order to read them:

1. **FunSearch** (DeepMind, 2023) — an LLM proposes *programs*, they are scored, the
   best go back into the prompt. The loop is the ancestor of yours.
   *Your question while reading: how exactly does the result get fed back?*

2. **EvoPrompting** (2023) — an LLM as the mutation operator inside an evolutionary
   loop over architectures.
   *Your question: does the model see performance history, or only code?*

3. **GENIUS** (2023) — an LLM used directly for NAS, closest to what you are doing.
   *Your question: how does it serialise an architecture into text, and how many seeds
   does it report?* You will copy or beat this design decision.

4. **OPRO** — "Large Language Models as Optimizers." The general framing: put the
   trajectory of past solutions and scores in the prompt and ask for a better one.
   This is your method's abstract form.

**The gap you are filling:** these report wins. None of them runs a controlled,
matched-budget, multi-seed comparison against regularized evolution on a tabular
benchmark. That is a real gap, but **verify it is still a gap on Thu 20 Aug** — a year
is a long time in this field.

---

## 7 · How your method actually works

Six steps, and the whole paper is these six steps done carefully:

1. **Seed** — evaluate 5–10 random architectures. Now you have a history.
2. **Serialise** — turn the history into text the model can reason about:
   ```
   arch: |nor_conv_3x3~0|+|skip_connect~0|none~1|+|...   accuracy: 91.2
   arch: |avg_pool_3x3~0|+|nor_conv_1x1~0|none~1|+|...   accuracy: 88.7
   ```
3. **Prompt** — "here are the architectures tried and their accuracies. Propose the
   next one, in this format." **No code generation.** That is your design choice.
4. **Parse** — extract the proposed architecture string. Validate it. Handle malformed
   output gracefully, because it will be malformed sometimes, and *how often* is itself
   a result worth reporting.
5. **Evaluate** — one table lookup. Append to history.
6. **Repeat** for N queries. Then run random, greedy and regularized evolution at the
   same N. Repeat all four across 5 seeds.

Table 1 is the mean ± std of the best accuracy found by each method at matched N.
That table is the paper.

---

## 8 · Why the honesty framing *is* the contribution

Your contribution statement ends: *"We characterise the regime in which LLM-guided
search outperforms random search, and the regime in which it does not."*

Given section 3 — a field whose credibility problem was papers that only reported
wins — a clean statement of where the method loses is not a weakness you are
confessing. **It is the thing the field is short of**, and it is what a reviewer will
find hard to reject.

It is also the best interview answer you will own. "What did you find?" — "That it
helps early, when history is informative, and stops helping once the budget is large
enough that random search catches up. Here is the crossover point."

---

## 9 · What could kill this paper

- **It never beats random.** Not fatal. Pivot the framing to "when and why LLM-guided
  NAS fails" — that is publishable. Decide by **27 Sep**, do not spend six weeks
  forcing a positive.
- **Someone published it already.** Check on **20 Aug**. If they did, you differentiate
  on the controlled comparison, which most skip.
- **Single-seed results.** Self-inflicted and fatal. Five seeds minimum on any headline
  number.
- **No regularized evolution baseline.** Self-inflicted and fatal. See section 5.

---

## Reading order

Do not read all four papers now. One per session, in this order, with the question
already written down:

| When | Paper | The one question |
|---|---|---|
| Next paper session | FunSearch | How does the result feed back into the prompt? |
| Same session | EvoPrompting (skim) | History, or only code? |
| Tue 18 Aug | GENIUS | How does it serialise? How many seeds? |
| Thu 20 Aug | arXiv search, 2025–26 | Has anyone already done the controlled comparison? |

You do not need to understand the whole area. You need to understand these four papers
and the six steps in section 7. That is the entire conceptual load of this project.
