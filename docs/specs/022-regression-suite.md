# Spec 022: regression suite (eval behavior snapshot)

## Purpose
Guard the eval's current behavior against silent drift. Later days will
edit the injector, runner, baseline and detectors; this suite re-runs
the full synthetic case set through the spec-005 runner with the
spec-008 rule baseline at fixed seeds and diffs every tally number and
inapplicability reason against a committed snapshot. A change in any of
those layers becomes a failing test that NAMES the drifted number. The
snapshot records actual behavior as of day 26; it does not re-validate
labels (milestone 6 review stays the label gate) and all counts stay
provisional.

## API
`run_regression(cases, seeds=REGRESSION_SEEDS) -> dict`

- `cases`: list of case dicts (raw parsed JSON), else ValueError. Every
  item must be a dict.
- `seeds`: tuple or list of ints, not bools, else ValueError.
- Returns `{'case_count': N, 'seeds': {str(seed): snapshot}}` where
  snapshot maps each error type (in ERROR_TYPES order) to
  `{applicable, detected, not_detected, inapplicable, false_flags,
  reasons}`. reasons is the spec-005 reasons dict. Deterministic for
  identical inputs.

`check_snapshot(live, expected) -> list of str`

- Both arguments must be dicts of the run_regression shape, else
  ValueError.
- Returns [] when identical, else one human-readable string per
  mismatch naming the seed, error type, field and both values (missing
  keys reported as absent). Never raises on content differences; it
  reports them.

`load_regression_cases(directory) -> list of dict`

- directory must exist, else ValueError. Reads every `*.json` file in
  sorted filename order and returns the raw dicts. Non-dict JSON raises
  ValueError naming the file.

`REGRESSION_SEEDS = (0, 1, 2)` - three fixed seeds so a seed-dependent
injector branch is covered too.

## Snapshot data
`data/regression/baseline-snapshot.json` holds the committed expected
output of `run_regression` over the 50 synthetic cases, written with
sorted keys and 2-space indent. Regenerating it is a deliberate act
(new snapshot commit with its own decision-log entry), never part of a
test run.

## Out of scope
LLM-auditor snapshots (needs a canned transport decision), percentages,
any label re-validation, procedure vocabulary.
