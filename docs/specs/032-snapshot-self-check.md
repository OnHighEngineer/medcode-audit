# Spec 032: snapshot self-check entry point

## Purpose
The five committed snapshots pin every lane, but verifying them means
running pytest. This spec adds one offline command that re-runs every
lane and diffs each live result against its committed snapshot,
printing one OK/drift line per lane, so a reviewer verifies the
committed numbers without pytest. Offline, canned transports,
deterministic; counts stay provisional.

## Function
`check_committed_snapshots(data_dir=None) -> dict` in regression.py

- data_dir: a directory holding synthetic/ and regression/; None means
  the repo's own data/ (resolved from this file's location, so the
  check works from any cwd). A missing directory raises ValueError.
- Loads cases with the spec-022 load_regression_cases, re-runs the
  baseline and llm lanes via run_regression, each noisy lane via
  run_regression(lane=...), and the cost lanes via run_llm_cost and
  run_llm_cost_by_type, and diffs each live result against its
  committed snapshot with the spec-022 check_snapshot.
- Returns {lane: [problems]} in SELF_CHECK_LANES order: baseline, llm,
  noisy_wrong_verdict, noisy_fabricated_quote, noisy_dropped_verdict,
  llm_cost, llm_cost_by_type. An empty list means the lane matches its
  committed snapshot.
- Additive only: no existing function, test or snapshot changes.

`main(argv=None) -> int`, also runnable as
`python -m medcode_audit.regression`

- Prints one line per lane in SELF_CHECK_LANES order: `<lane>: OK`, or
  `<lane>: DRIFT (N problems)` followed by each problem on its own
  indented line. Returns 0 when every lane is OK, 1 on any drift. Any
  argument raises ValueError.

## Non-goals
Updating snapshots from this command (the spec-022 process owns
snapshot updates: intentional change, both Python versions green,
decision logged); re-validating labels (milestone 6); new lanes.
