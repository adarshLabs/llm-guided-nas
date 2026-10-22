# Prompt format ablation — a null result

**29 Sep 2026** · `run_id = 20260929T022356-s42` · NATS-Bench-TSS, CIFAR-10, `hp='200'`, `is_random=False`

Does the way the search state is presented to the model change what it proposes?

**No. Not measurably, and not at all.** Three structurally unrelated encodings of the
same five architectures produced bit-identical search trajectories.

---

## SETUP

| | |
|---|---|
| Model | `gemini-3.1-flash-lite` · temperature 1.0 · `seed=42` |
| Sampler seed | 42 — all three arms start from the identical five architectures |
| Seed set accuracies | 73.03 · 75.58 · 86.51 · 86.65 · **92.74** |
| Budget | `MAX_QUERIES=5` distinct architectures · `MAX_CALLS=15` |
| Duplicate handling | a repeat proposal is logged and does **not** consume a query |
| History | full — every evaluated architecture stays in the prompt, no eviction |
| Output format | fixed across all arms: the NATS string, parsed by `ARCH_RE` |

**Only the input encoding varies.** The three arms differ on two axes: how explicitly
the target node is named, and how far the representation sits from natural language.

| Arm | Form | Target node |
|---|---|---|
| `as_nats` | `\|nor_conv_3x3~0\|+\|...` — positional, delimiter-based | implicit, from position between `+` |
| `as_adjacency` | `0 -> 1 : nor_conv_3x3`, six lines | explicit; line order carries no meaning |
| `as_prose` | *"Node 1 takes a 3x3 convolution from the input."* | explicit, in words; no delimiters |

---

## RESULT

| Arm | LLM calls | Distinct queries | Duplicates | Best found | Stop reason |
|---|---|---|---|---|---|
| `as_nats` | 15 | **2** | 13 | **93.76** | call_cap |
| `as_adjacency` | 15 | **2** | 13 | **93.76** | call_cap |
| `as_prose` | 15 | **2** | 13 | **93.76** | call_cap |

**The trajectories are identical, not merely similar.** Every arm proposed:

1. call 0 → idx **1462**, all six edges `nor_conv_3x3`, **93.76%**
2. call 1 → idx **7632**, the same cell with the last edge swapped to `nor_conv_1x1`, **93.56%**
3. calls 2–14 → idx 1462 again, thirteen times, until the call cap

**Two distinct architectures were ever proposed, across all three arms and 45 LLM calls.**
39 of those 45 calls (86.7%) were repeats.

---

## WHAT IT MEANS

**1. The format null is real, not an artefact of a badly designed ablation.**

The earlier concern (6 Sep) was that an ablation over three cosmetic variants of one
representation returns nothing by construction — which was true of `as_adjacency` vs
`as_table`, since those are the same triples with different whitespace. That is fixed
here: prose shares no surface form with the NATS string. It still returns nothing.
**The proposal is not conditioned on the representation.**

**2. The knowledge is parametric, not lexical.**

The prediction was that if the all-3×3 prior were memorisation of the NAS-Bench-201
*string format*, a prose prompt — which resembles no paper in the literature — should
degrade it most. Prose degraded it by zero. So the model is not pattern-matching the
notation; it holds the strong cell as a fact about the world, retrievable through any
encoding.

**3. The feedback loop contributes nothing measurable.**

The model returned 1462 thirteen times while 1462 was present in its own history and the
prompt explicitly instructed it not to repeat anything listed. Whatever the history block
is doing, it is not steering the proposal.

**4. Against the random baseline, the result is sample efficiency with a hard ceiling.**

`random_baseline.md`: 100 random draws, seed 42 → mean 88.303, **max 93.770**.
The LLM reached 93.76 on its **first** query and never improved on it. Verified global
optimum for this space is **94.37**.

So: one query to match what random search needs ~100 draws to find, and then no search
behaviour at all — 0.61 points short of the optimum, permanently. On this benchmark,
"LLM-guided search" is a one-shot prior lookup with a degenerate loop attached.

This is the regime the abstract promises to characterise as the one in which the method
*does not* outperform. It is a result, not a failure.

---

## ONE BUG THIS EXPOSED

**Retrying an unchanged prompt at a fixed seed is a provable no-op.**

`llm_seed` is fixed, and the prompt is only rebuilt after a *successful* query. So on a
duplicate, the next call receives byte-identical input with the same seed — the same
output is guaranteed by construction, not merely likely. That is why all three arms
burned 13 calls and stopped at `call_cap` with `query=2` of a 5-query budget.

The duplicate guard fixed the query accounting and, in doing so, revealed that the
controller has no escape mechanism. A duplicate must change something before the retry.
Two candidate fixes, and they test different things — they should be run as separate
arms, not combined:

- **Exclusion list.** Pass the rejected architectures back in the prompt as an explicit
  "do not propose any of the following" block. Tests instruction-following.
- **Seed variation.** `seed = SEED + calls`, making a retry an actual resample. Tests
  whether the output distribution has mass anywhere else at all.

---

## THREATS TO VALIDITY — stated before anyone asks

**Contamination is the dominant threat and it is not yet excluded.** NAS-Bench-201 is
public, widely published, and all-3×3 is its textbook strong cell. Finding 2 says the
knowledge survives re-encoding, which is *consistent* with contamination and does not
distinguish it from genuine architectural reasoning.

**n = 1 per arm.** With the seed fixed, each arm is a single deterministic sample. The
across-arm identity is real signal — different prompts yielding identical outputs cannot
be a seeding artefact — but there is no within-arm variance estimate. Multi-seed is
required before any of this enters a table.

**One model, one size.** `gemini-3.1-flash-lite`. The prior may be weaker in a smaller
model and stronger in a larger one; neither is tested.

**A seeded LLM call is best-effort.** Provider-side model updates break reproducibility.
The full version string should be pinned rather than the `-lite` alias.

---

## NEXT EXPERIMENT — neutral labels

Now the highest-value run available, because the format null makes it the only remaining
way to separate "the model has memorised this benchmark" from "the model reasons about
architectures."

Protocol, fixed in advance:

1. Replace the operation names in `OPS` with `op_a`…`op_e`, holding the mapping to real
   operations constant and private to the harness.
2. Substitute the same labels in the prompt's operation list and its worked example.
3. Change nothing else — same seed set, same budget, same seeds, one arm per format.
4. Record the prediction before running.

**Prediction, written now:** if 1462 still comes back, contamination is complete and the
honest conclusion is that NAS-Bench-201 cannot be used to evaluate LLM-guided NAS at all.
That is a methodological contribution and it is worth more than a 0.2-point win would have
been.

---

## LOGGING DEFECTS IN `search_runs.jsonl`

Recorded because they will silently corrupt any later analysis.

- **`run_id` is shared across all three arms.** It is generated once in `main()` with the
  format loop inside, so only `fmt` separates the arms. Move it inside the loop or append
  `FMT.__name__`.
- **Grouping by `fmt` alone already gives a wrong answer.** The file holds five earlier
  partial runs. Aggregating all `as_adjacency` rows returns calls=20, queries=5 — mixing
  the aborted `022245` run into this one. **Every analysis must filter on
  `run_id == '20260929T022356-s42'`.**
- **Schema drift.** The 25 Sep `-real` run carries `arm`, `best_so_far`, `n_unique`,
  `dims_explored`, `n_fail`; nothing since does. Recompute everywhere or drop them.
- **Three orphan runs** (`022030`, `022151`, `022245`) have no `end` row, and there is no
  `start` row either — so a crashed run is indistinguishable from an interrupted one.
  Log `start`, and filter on `start`+`end` when analysing.
