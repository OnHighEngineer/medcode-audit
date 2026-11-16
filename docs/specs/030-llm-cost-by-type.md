# Spec 030: per-error-type cost split for the LLM lane

## Purpose
Spec 028 snapshots the llm lane's total transport traffic per seed, but
the eval asks one question per case per error type, so a single total
hides where the volume concentrates. This spec splits the same
accounting by error type - one tracked run per type - so the snapshot
shows, for example, that unsupported_code questions carry the most
prompt characters. Offline, canned replies only; numbers are synthetic
accounting, provisional like every other count.

## Function
`run_llm_cost_by_type(cases, seeds=REGRESSION_SEEDS) -> dict` in
regression.py

- Same argument validation as run_llm_cost: cases must be a list of
  dicts, seeds a tuple/list of ints; anything else raises ValueError.
- Per seed, per error type in schema.ERROR_TYPES order: wrap a fresh
  `make_gold_transport(cases)` in `make_tracking_transport` with the
  same deterministic step clock as run_llm_cost (latency 1 per call),
  run the spec-005 eval restricted to that one type
  (`run_eval(..., error_types=(etype,), seed=seed)`), and record
  `summarize_records(records)` - the spec-018 summary shape.
- Returns {'case_count': n, 'seeds': {str(seed): {etype: summary}}} -
  nested one level deeper than run_llm_cost; the existing check_snapshot
  recursive diff works on it unchanged.
- A type that is inapplicable on every case gets a zero-call summary
  (calls 0, mean_latency None) - the spec-018 summary already allows
  this.
- Invariant: per-type sums equal the run_llm_cost totals per seed
  (calls, prompt_chars, reply_chars), because the split asks exactly
  the same (case, error type) questions. Pinned by a test.
- Records stay beside the run (spec-018 rule): run_eval, the tally
  snapshots and the frozen run shape are untouched.

## Snapshot
data/regression/llm-cost-by-type-snapshot.json - committed output of
run_llm_cost_by_type on the 50 synthetic cases at REGRESSION_SEEDS.
Drift in prompt construction, canned reply size, per-type
applicability or call count fails the test with the drifted number
named. Updating the snapshot follows the spec-022 process: intentional
change, both Python versions green, decision logged.

## Non-goals
Per-type cost on baseline or noisy lanes (baseline has no transport;
noisy lanes abort some seeds by design). Splitting a single combined
run's records by type after the fact (the tracking transport sees only
prompts; per-type runs are the attribution path). Real token counts or
prices (offline character accounting only, per spec 018).
