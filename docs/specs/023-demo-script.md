# Spec 023: demo entry point (offline, baseline)

## Purpose
One command that runs the whole pipeline end to end on the committed
synthetic cases and prints the assembled eval report a reviewer would
read: spec-005 run with the spec-008 rule baseline, spec-017 failure
analysis, spec-019 report. Plan item 27's demo half. Offline and
deterministic: no transports, no network, no provider anything.

## API
`run_demo(case_dir=None, seed=DEMO_SEED) -> str`

- `case_dir`: directory of case JSON files. None means the repo's own
  data/synthetic (resolved from this file's location, so the demo works
  from any cwd). A missing directory raises ValueError (via
  load_regression_cases).
- `seed`: int, not bool, else ValueError. DEMO_SEED = 0.
- Returns the spec-019 report markdown for
  `run_eval(cases, audit_baseline, seed=seed)` with
  `analyze_run(run, cases)` attached. Loads cases with the spec-022
  `load_regression_cases` (raw dicts, sorted filenames) so the demo and
  the regression suite read the same bytes the same way. Deterministic
  for identical inputs; carries the provisional header; no percentages.

`main() -> int`

- Prints `run_demo()` to stdout, returns 0. Kept thin so the spec-019
  wording stays the only output contract; argparse, flags and pretty
  consoles stay out.

## Out of scope
LLM-auditor demo output (a canned-reply demo could read as a real model
result; revisit if a later day wants it), HTML, any live provider call,
percentages, procedure vocabulary.
