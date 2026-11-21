# Spec 035: self-check --only filter

Status: implemented (day 39, 2026-11-21).

## Problem
`python -m medcode_audit.regression` (spec 032) always re-runs all nine
lanes. While iterating on one snapshot that costs most of a minute of
eval runs. A reviewer fixing one lane's drift wants to re-check just
that lane.

## Contract
`python -m medcode_audit.regression --only LANE [--only LANE ...]`
re-checks only the named lanes:

- Each LANE must be a member of SELF_CHECK_LANES; an unknown lane name
  raises ValueError, as does `--only` with no value and any other
  argument (the spec-032 unknown-argument rule is unchanged).
- Only the named lanes run: their evals execute, their snapshot or
  artifact files are read, and one OK/drift line prints per named lane
  in SELF_CHECK_LANES order regardless of argument order. Duplicate
  names collapse.
- Exit code is 0 when every named lane matches, 1 on any drift, the
  spec-032 rule scoped to the named lanes.
- No arguments at all keeps the spec-032 behavior byte-for-byte: every
  lane runs, nine lines print.

`check_committed_snapshots(data_dir=None, reviews_dir=None, only=None)`
gains the optional `only` parameter. With `only=None` the spec-032
return contract is unchanged: every lane key in SELF_CHECK_LANES order.
With a tuple of lane names it returns only those lanes, in
SELF_CHECK_LANES order, and skips the eval runs and file reads of the
lanes not named. Unknown names raise ValueError.

## Non-goals
- No lane globbing or prefix matching; exact names only.
- No drift-fixing mode (spec 032 already rejected it).
- No change to what any lane checks or to any snapshot/artifact file.
