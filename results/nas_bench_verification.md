# NATS-Bench lookup — verification against published optima

**Date:** 3 September 2026
**Benchmark:** NATS-Bench topology search space (`tss`), `NATS-tss-v1_0-3ffb9-simple`,
loaded with `create(None, 'tss', fast_mode=True)` from `$TORCH_HOME`
**Query settings:** `hp='200'` (full 200-epoch training) and `is_random=False`
(deterministic mean over seeds, not a single random seed)
**Method:** exhaustive scan of all 15,625 architectures on each of the three
datasets, taking the argmax of `test-accuracy`. `clear_params(i)` called per
index to keep resident memory bounded.

## Result — all three match

| Dataset | Best arch (index) | My lookup | Published optimum | Delta |
|---|---|---|---|---|
| CIFAR-10 | 6111 | **94.37%** | 94.37% | 0.00 |
| CIFAR-100 | 9930 | **73.51%** | 73.51% | 0.00 |
| ImageNet16-120 | 857 | **47.31%** | 47.31% | 0.00 |

Published figures are the global optima reported for the NAS-Bench-201 space
(Dong & Yang, ICLR 2020, arXiv:2001.00326). NATS-Bench's topology space is the
same 15,625-architecture space, so the optima are directly comparable.

## What this establishes

The lookup returns the same global optimum the original authors found, on every
dataset, across the entire space — not merely that three cells are populated.
Any accuracy this pipeline reports downstream can be treated as the benchmark's
own number.

This closes the Phase 0 requirement that the benchmark be verified before any
search result is built on top of it.

## Notes

- An earlier smoke test queried at the default `hp='12'` and returned ~10% on
  CIFAR-10 — chance level, and matching nothing published. That was a
  12-epoch result, not a failure of the lookup. **Always pass `hp='200'` when
  comparing against published numbers.**
- `is_random=False` matters for reproducibility: with the default, repeated
  calls return different seeds and the argmax is not stable.
- `nats_bench`'s `pickle_load` appends a second `.pbz2` when a file is missing,
  so a missing archive surfaces as a mangled filename rather than "not found."
  Worth remembering if the path ever moves.