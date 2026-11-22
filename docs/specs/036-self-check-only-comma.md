# Spec 036: comma-separated lane names in self-check --only

Status: implemented (day 40, 2026-11-22).

## Problem
Spec 035's `--only LANE` repeats the flag per lane:
`--only baseline --only llm_cost`. The common CLI convention
`--only baseline,llm_cost` does not parse - the whole string fails
lane validation as one unknown name.

## Contract
The value of `--only` splits on commas; each segment is one lane name:

- `--only baseline,llm_cost` behaves exactly like
  `--only baseline --only llm_cost`: both lanes run, lines print in
  SELF_CHECK_LANES order, exit 0/1 scoped to them.
- Comma values mix freely with repeated flags
  (`--only demo_html,baseline --only llm_cost`).
- Every segment must be an exact lane name. An empty segment
  (`--only baseline,`, `--only ,baseline`, `--only ,`), an unknown
  name, and whitespace-padded names (`--only 'baseline, llm_cost'`)
  all raise ValueError. No trimming, no globbing - the spec-035
  exact-names rule is unchanged.
- `check_committed_snapshots(only=...)` still takes exact lane names;
  comma parsing lives in the CLI argument layer only, so the library
  contract is untouched.

## Non-goals
- No whitespace tolerance inside values.
- No change to lane execution, output order or exit codes.
