# Day 21: cost/latency at the transport boundary (provisional)

Command: `run_eval` over all 50 checked-in cases with the spec-009 LLM
auditor on a canned transport (every claimed code answered UNSUPPORTED,
no missed codes - a placeholder reply, not an auditor candidate), the
transport wrapped in `make_tracking_transport` with a scripted clock
stepping 1 per reading, seed 0, all five error types. Reproduce with the
same inputs; every piece is deterministic. No live provider was called
and no key was used or requested (Oct 21 rule).

Cost/latency summary (spec 018):

```
COST/LATENCY (PROVISIONAL): character counts and transport timings at the spec-009 boundary; synthetic accounting only, not trusted scores.
calls 119
latency: total 119, mean 1.0
characters: prompt 95602 in, reply 10721 out
```

Runner counts under the canned transport (unchanged plumbing, records
kept outside the frozen run shape):

```
PROVISIONAL: synthetic labels, no clinical review yet (milestone 6). Counts only, not trusted scores.
seed 0
wrong_code: not implemented (deferred_unverified_mapping), 50 cases skipped
upcoding: detected 17/17, not detected 0, inapplicable 33, false flags on gold claims 4
unsupported_code: detected 48/48, not detected 0, inapplicable 2, false flags on gold claims 45
missed_code: detected 0/38, not detected 38, inapplicable 12, false flags on gold claims 7
negated_condition: detected 16/16, not detected 0, inapplicable 34, false flags on gold claims 10
```

## Read this before the numbers
The mechanics are the result, not the numbers: one transport call per
applicable row (17 + 48 + 38 + 16 = 119; wrong_code stays deferred),
each call accounted with prompt/reply character counts and a clock
delta. The clock here is scripted (1 unit per reading), so latency
figures demonstrate the accounting, not model speed - real timings need
a live provider, which stays out of scope offline. Character counts are
the offline unit: exact and reproducible, but not provider tokens, so
they understate nothing and approximate nothing; they are simply what
crossed the boundary. The rule baseline makes zero transport calls by
construction, so an LLM auditor's cost is always on top of detection
parity, never instead of it. Counts remain provisional until the
milestone 6 clinical review.
