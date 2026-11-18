# Day-36 review: noisy-lane fail-closed evidence

The three spec-026 noisy lanes inject one deterministic corruption per
canned reply to pin BOTH halves of fail-closed behavior: wrong replies
that pass validation surface as false flags, and malformed replies are
rejected with a named validation error. Counts stay provisional.

Artifact: `data/regression/noisy-snapshot.json` (spec 026), produced by
`run_regression(cases, lane=...)` on the 50 committed synthetic cases.
Read it with `PYTHONPATH=src python -m medcode_audit.regression`
(spec 032: one OK/drift line per lane) or
`pytest tests/test_noisy_regression.py`.

## Committed values (quoted from the artifact)
### noisy_wrong_verdict (flows through validation; surfaces as false flags)
Seed 0 (seeds 1 and 2 identical):
- missed_code: applicable 38, detected 38, not_detected 0, false_flags 7
- negated_condition: applicable 16, detected 16, not_detected 0, false_flags 10
- unsupported_code: applicable 48, detected 48, not_detected 0, false_flags 38
- upcoding: applicable 17, detected 17, not_detected 0, false_flags 4
- wrong_code: applicable 0 (inapplicable on all 50; reason
  deferred_unverified_mapping)

Every applicable case is still detected on every seed
(detected == applicable, not_detected 0) and the flipped first gold
claim shows up as false flags: 59 per seed (7 + 10 + 38 + 4).

### noisy_fabricated_quote (rejected; eval aborts)
Every seed records exactly:
`validation_error: evidence_quote must be a verbatim note substring`

### noisy_dropped_verdict (rejected; eval aborts)
Every seed records exactly:
`validation_error: verdicts must cover exactly the claimed codes`

## What this guards
A change that lets a fabricated quote or a partial verdict list through
spec-007 validation flips a rejecting lane from its named abort to a
tally, and a change that swallows wrong verdicts drops the false-flag
count - both fail `tests/test_noisy_regression.py` (and the spec-032
self-check) with the drift named. It says nothing about real model
behavior; all labels remain provisional pending the milestone 6 review.
