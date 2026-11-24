# Spec 038: equals form for self-check --only

Status: implemented (day 42, 2026-11-24).

## Problem
Specs 035+036 accept `--only LANE` and `--only LANE,LANE`, but the
other common CLI convention, `--only=LANE`, does not parse: the whole
token falls through to the unknown-argument rule and raises
ValueError. A reviewer reaching for the argparse-style equals form
hits an avoidable dead end in a flag that already exists.

## Contract
`python -m medcode_audit.regression --only=LANE` behaves exactly like
`--only LANE`:

- The token `--only=VALUE` is the equals form of `--only VALUE`. The
  VALUE splits on commas under the spec-036 rules, so
  `--only=baseline,llm_cost` equals `--only baseline,llm_cost`.
- The equals form mixes freely with the space form
  (`--only=demo_html --only llm_cost`); lines print in
  SELF_CHECK_LANES order, exit 0/1 scoped to the named lanes.
- `--only=` with an empty value raises ValueError (the empty segment
  fails the spec-036 exact-name rule, like `--only ,baseline`).
- Every other spec-035/036 rule is unchanged: exact names, no
  trimming, no globbing, unknown names raise ValueError.
- `--list` stays the spec-037 single-argument mode: combining it with
  the equals form raises ValueError.
- `check_committed_snapshots(only=...)` still takes exact lane names;
  equals parsing lives in the CLI argument layer only, so the library
  contract is untouched.

## Non-goals
- No abbreviated flag forms (`--o`, `-o`); the full flag name only.
- No `=` handling for `--list` (it takes no value; `--list=x` stays an
  unknown argument and raises).
- No change to lane execution, output order or exit codes.
