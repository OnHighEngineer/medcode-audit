# Spec 039: demo --seed flag

Status: implemented (day 43, 2026-11-25).

## Problem
The regression suite pins the eval at seeds 0, 1 and 2 (spec 022), but
the demo CLI prints only the DEMO_SEED (0) report. A reviewer who wants
to read the full report - tally plus failure analysis - for seed 1 or
2 must call run_demo(seed=N) from Python; every run_demo* function
already takes the seed, only the CLI withholds it.

## Contract
`python -m medcode_audit.demo --seed N` runs the whole demo at seed N:

- `--seed N` and the equals form `--seed=N` (spec 038's convention)
  both set the seed. The value must be an optionally-signed decimal
  integer (`-?` followed by digits only); anything else - a bare
  `--seed`, an empty `--seed=`, a float, a name, a `+`-prefixed or
  underscore-grouped number - raises ValueError.
- The seed applies to every output path: the markdown report, `--cost`
  and `--cost-by-type` blocks, and the `--html` page. Repeated `--seed`
  flags collapse last-wins.
- No `--seed` keeps today's behavior byte-identical: seed DEMO_SEED,
  every frozen demo test untouched. The spec-033 exclusivity and
  unknown-argument rules are unchanged.
- No new validation beyond the integer shape: any int the library
  accepts is accepted, matching run_demo's contract.

## Non-goals
- A --cases flag (the committed synthetic directory stays the only CLI
  data source; the library already takes case_dir).
- Restricting the seed to the snapshotted 0-2 range (the library
  accepts any int; the CLI stays as permissive as the function).
- Any change to default outputs, snapshot files or lane behavior.
