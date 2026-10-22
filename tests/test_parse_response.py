"""Negative tests for parse_response — the branch 70 live calls never exercised.

Every search row logged to date has parse_ok=true, so none of the five rejection
paths in parse_response has ever fired in production. This file fires all of them.

Zero API calls: parse_response is a pure function of a string.

Run:  python tests/test_parse_response.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from controller import parse_response  # noqa: E402

VALID = ("|nor_conv_3x3~0|+|nor_conv_3x3~0|nor_conv_3x3~1|"
         "+|nor_conv_3x3~0|nor_conv_3x3~1|nor_conv_3x3~2|")

# (name, input, should_parse)
CASES = [
    # --- accepted ---
    ("valid 4-node string",      VALID,                                  True),
    ("markdown fenced",          f"```\n{VALID}\n```",                   True),
    ("explanation then string",  f"Here is my answer: {VALID}",          True),
    ("trailing newline",         VALID + "\n",                           True),

    # --- rejected: no arch-shaped substring ---
    ("None input",               None,                                   False),
    ("empty string",             "",                                     False),
    ("prose, no arch",           "I would use 3x3 convolutions.",        False),
    ("refusal",                  "I cannot determine a better cell.",    False),

    # --- rejected: wrong edge set ---
    ("3-node cell (short)",
     "|nor_conv_3x3~0|+|nor_conv_3x3~0|nor_conv_3x3~1|",                 False),
    ("5-node cell (long)",
     VALID + "+|skip_connect~0|skip_connect~1|skip_connect~2|skip_connect~3|",
     False),
    ("duplicate source edge",
     "|nor_conv_3x3~0|+|nor_conv_3x3~0|nor_conv_3x3~0|"
     "+|nor_conv_3x3~0|nor_conv_3x3~1|nor_conv_3x3~2|",                  False),

    # --- rejected: operation outside the space ---
    ("op outside the space",
     "|bogus_op~0|+|nor_conv_3x3~0|nor_conv_3x3~1|"
     "+|nor_conv_3x3~0|nor_conv_3x3~1|nor_conv_3x3~2|",                  False),
    ("plausible but wrong op name",
     "|conv_3x3~0|+|nor_conv_3x3~0|nor_conv_3x3~1|"
     "+|nor_conv_3x3~0|nor_conv_3x3~1|nor_conv_3x3~2|",                  False),

    # --- rejected: malformed ---
    ("truncated mid-string",     "|nor_conv_3x3~0|+|nor_conv_3x3~0|nor_c", False),
    ("pipes only",               "||||",                                  False),
]


def main():
    width = max(len(name) for name, _, _ in CASES)
    failures = 0

    for name, text, should_parse in CASES:
        try:
            got = parse_response(text) is not None
        except Exception as exc:                      # parse_response must never raise
            print(f"{name:<{width}}  RAISED {type(exc).__name__}: {exc}")
            failures += 1
            continue

        ok = got == should_parse
        failures += not ok
        flag = "" if ok else "   <-- MISMATCH"
        print(f"{name:<{width}}  expect={str(should_parse):<5} got={str(got):<5}{flag}")

    print(f"\n{len(CASES) - failures}/{len(CASES)} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
