# Spec 028: cost accounting for the LLM regression lane

## Purpose
The spec-024 llm lane snapshots eval tallies but records nothing about
the transport traffic it generates. Spec 018 built the accounting
primitive (make_tracking_transport: character counts plus an injected
clock, records beside the run). This spec wires that primitive into the
llm lane as a separate, deterministic snapshot - so a change that
silently doubles prompt size or call count becomes a failing test that
names the drifted number. Offline, canned replies only; no provider,
no spend. Numbers are synthetic accounting, provisional like every
other count.

## Function
`run_llm_cost(cases, seeds=REGRESSION_SEEDS) -> dict` in regression.py

- Same argument validation as run_regression: cases must be a list of
  dicts, seeds a tuple/list of ints; anything else raises ValueError.
- Per seed: wrap `make_gold_transport(cases)` in
  `make_tracking_transport` with a deterministic step clock (latency 1
  per call), run the spec-005 eval through `make_llm_auditor`, and
  record `summarize_records(records)` - the spec-018 summary shape
  (calls, total_latency, mean_latency, prompt_chars, reply_chars).
- Returns {'case_count': n, 'seeds': {str(seed): summary}} - the same
  envelope as run_regression so the existing check_snapshot diff works
  on it unchanged.
- Records stay beside the run (spec-018 rule): run_eval, the tally
  snapshots and the frozen run shape are untouched.

## Snapshot
data/regression/llm-cost-snapshot.json - committed output of
run_llm_cost on the 50 synthetic cases at REGRESSION_SEEDS. Drift in
prompt construction, canned reply size or call count fails the test
with the drifted number named. Updating the snapshot follows the
spec-022 process: intentional change, both Python versions green,
decision logged.

## Non-goals
Cost tracking on baseline or noisy lanes (baseline has no transport;
noisy lanes abort some seeds by design). Real token counts or prices
(offline character accounting only, per spec 018).
