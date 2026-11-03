# Day 23: assembled eval report (provisional)

Command: `run_eval` over all 50 checked-in cases with the spec-008 rule
baseline, seed 0, all five error types; then `generate_report(run,
analyze_run(run, cases), [])` (spec 019). Reproduce with the same
inputs; every stage is deterministic. The empty records list renders the
honest zero-call cost section - the rule baseline crosses no transport
boundary. wrong_code stays deferred.

Generated report (verbatim `generate_report` output):

```
# medcode-audit eval report

EVAL REPORT (PROVISIONAL): synthetic labels, no clinical review yet (milestone 6). Counts only, not trusted scores.

seed 0

## Runner summary

```
PROVISIONAL: synthetic labels, no clinical review yet (milestone 6). Counts only, not trusted scores.
seed 0
wrong_code: not implemented (deferred_unverified_mapping), 50 cases skipped
upcoding: detected 17/17, not detected 0, inapplicable 33, false flags on gold claims 0
unsupported_code: detected 48/48, not detected 0, inapplicable 2, false flags on gold claims 0
missed_code: detected 38/38, not detected 0, inapplicable 12, false flags on gold claims 0
negated_condition: detected 16/16, not detected 0, inapplicable 34, false flags on gold claims 0
```

## Failure analysis

```
FAILURE ANALYSIS (PROVISIONAL): synthetic labels, no clinical review yet (milestone 6). Explains where failures concentrate; counts only, not trusted scores.
seed 0

error type: wrong_code
not detected: none
false flags on gold claims: none
inapplicable: deferred_unverified_mapping 50

error type: upcoding
not detected: none
false flags on gold claims: none
inapplicable: no_ordinal_gold_code 33

error type: unsupported_code
not detected: none
false flags on gold claims: none
inapplicable: no_unmentioned_condition 2

error type: missed_code
not detected: none
false flags on gold claims: none
inapplicable: no_gold_code 12

error type: negated_condition
not detected: none
false flags on gold claims: none
inapplicable: no_negated_target 34
```

## Cost/latency

```
COST/LATENCY (PROVISIONAL): character counts and transport timings at the spec-009 boundary; synthetic accounting only, not trusted scores.
calls 0
no calls recorded
```
```

## Read this before the numbers
The generator assembles; it does not recompute. Every number above is
rendered verbatim from the frozen module formatters (spec 005 tally,
spec 017 strata, spec 018 accounting), so the report cannot drift from
the pieces a reviewer would check separately. Detection counts match the
day-19 review exactly; the failure analysis shows an all-green run with
empty breakdowns, which is the expected template-flattered baseline
picture, not a generalization claim. Counts remain provisional until the
milestone 6 clinical review.
