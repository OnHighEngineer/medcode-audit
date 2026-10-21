# Day 9: rule baseline eval (provisional)

Command: `run_eval` over all 50 checked-in cases with `audit_baseline`, seed 0,
all five error types. Reproduce with the same inputs; the runner is
deterministic.

```
PROVISIONAL: synthetic labels, no clinical review yet (milestone 6). Counts only, not trusted scores.
seed 0
wrong_code: not implemented (deferred_unverified_mapping), 50 cases skipped
upcoding: not implemented (deferred_unverified_mapping), 50 cases skipped
unsupported_code: detected 48/48, not detected 0, inapplicable 2, false flags on gold claims 0
missed_code: detected 38/38, not detected 0, inapplicable 12, false flags on gold claims 0
negated_condition: detected 16/16, not detected 0, inapplicable 34, false flags on gold claims 0
```

## Read this before the numbers
The baseline detects every injected error on this set. That is expected, not a
result: the goldset's closed sentences are the same templates the baseline
reads, and the prose notes use the same five condition phrases. The baseline
has no paraphrase or general negation handling, and the labels it is scored
against are still provisional (milestone 6 review pending). These counts are a
floor for the LLM auditor to explain, not evidence the problem is solved.
