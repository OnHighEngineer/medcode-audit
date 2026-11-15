# Day-32 review: LLM-lane cost snapshot

COST/LATENCY (PROVISIONAL): character counts and transport timings at
the spec-009 boundary; synthetic accounting only, not trusted scores.

Artifact: `data/regression/llm-cost-snapshot.json` (spec 028), produced
by `run_llm_cost` on the 50 committed synthetic cases. Read it with
`PYTHONPATH=src python -m medcode_audit.demo --cost` (spec 029) or
`pytest tests/test_llm_cost.py`.

## What the numbers are
Per seed the llm lane runs the spec-005 eval through the spec-024
gold-truth canned transport, wrapped in the spec-018 tracking
transport with a deterministic step clock. A "call" is one transport
round trip (one auditor question about one injected case variant);
characters are prompt/reply lengths - the offline proxy for tokens;
latency is 1 per call by construction of the clock.

## Committed values (quoted from the artifact, seed 0 / 1 / 2)
- calls: 119 / 119 / 119
- prompt_chars: 95602 / 95586 / 95646
- reply_chars: 15586 / 15597 / 15630
- total_latency: 119 / 119 / 119 (mean 1.0)

Call count is identical across seeds (the eval asks the same number of
questions; only which variant is injected rotates), while character
counts drift by a few dozen as different seeded wrappers change note
wording.

## What this guards
A change that silently alters prompt construction, canned reply size or
call count fails `tests/test_llm_cost.py` with the drifted number named.
It says nothing about real provider cost or model quality, and all
labels remain provisional pending the milestone 6 review.
