# Spec 037: self-check --list flag

Status: implemented (day 41, 2026-11-23).

## Problem
Specs 035+036 let a reviewer re-check named lanes with `--only`, but
the lane names live only in SELF_CHECK_LANES and the spec text. A
reviewer who does not remember the exact names (noisy_wrong_verdict or
noisy-wrong-verdict?) has no offline way to discover them short of
reading source.

## Contract
`python -m medcode_audit.regression --list` prints every lane name in
SELF_CHECK_LANES order, one per line, and exits 0. It runs no lane:
no eval executes, no snapshot or artifact file is read.

- `--list` must be the only argument. Combined with `--only`, with
  another `--list`, or with anything else it raises ValueError under
  the spec-032 unknown-argument rule.
- No arguments keeps the spec-032 behavior byte-for-byte; `--only`
  keeps the spec-035/036 behavior byte-for-byte.

## Non-goals
- No descriptions beside the names (the specs carry those; one name
  per line stays script-friendly).
- No lane execution of any kind in list mode.
