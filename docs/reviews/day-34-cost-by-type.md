# Day-34 review: LLM-lane cost by error type

COST/LATENCY (PROVISIONAL): character counts and transport timings at
the spec-009 boundary; synthetic accounting only, not trusted scores.

Artifact: `data/regression/llm-cost-by-type-snapshot.json` (spec 030),
produced by `run_llm_cost_by_type` on the 50 committed synthetic cases.
Read it with `PYTHONPATH=src python -m medcode_audit.demo --cost-by-type`
(spec 031) or `pytest tests/test_cost_by_type.py`.

## What the numbers are
Per seed the llm lane runs one spec-005 eval per error type, each
through its own spec-024 gold-truth canned transport wrapped in the
spec-018 tracking transport with the same deterministic step clock
(latency 1 per call). A type that is inapplicable on every case gets a
zero-call summary. The per-type sums equal the spec-028 totals exactly
on every seed, because the split asks exactly the same (case, error
type) questions.

## Committed values (quoted from the artifact, seed 0)
- unsupported_code: calls 48, prompt_chars 38509, reply_chars 8806
- missed_code: calls 38, prompt_chars 30157, reply_chars 2391
- upcoding: calls 17, prompt_chars 13696, reply_chars 1931
- negated_condition: calls 16, prompt_chars 13240, reply_chars 2458
- wrong_code: calls 0, prompt_chars 0, reply_chars 0

unsupported_code carries the most transport volume: 48 of the 119 calls
and 38509 of the 95602 prompt characters on seed 0 (same shape on seeds
1 and 2). wrong_code is inapplicable on all 50 cases - the synthetic
set injects no wrong_code variant - so it records a zero-call summary
on every seed.

## What this guards
A change that silently alters per-type prompt construction, canned
reply size, per-type applicability or call count fails
`tests/test_cost_by_type.py` with the drifted number named. It says
nothing about real provider cost or model quality, and all labels
remain provisional pending the milestone 6 review.
