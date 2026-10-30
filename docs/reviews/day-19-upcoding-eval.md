# Day 19: upcoding eval (provisional)

Command: `run_eval` over all 50 checked-in cases with `audit_baseline`, seed
0, all five error types. Reproduce with the same inputs; the runner is
deterministic.

```
PROVISIONAL: synthetic labels, no clinical review yet (milestone 6). Counts only, not trusted scores.
seed 0
wrong_code: not implemented (deferred_unverified_mapping), 50 cases skipped
upcoding: detected 17/17, not detected 0, inapplicable 33, false flags on gold claims 0
unsupported_code: detected 48/48, not detected 0, inapplicable 2, false flags on gold claims 0
missed_code: detected 38/38, not detected 0, inapplicable 12, false flags on gold claims 0
negated_condition: detected 16/16, not detected 0, inapplicable 34, false flags on gold claims 0
```

## Read this before the numbers
The baseline detects every injected upcoding on this set. That is expected,
not a result: the injection replaces an affirmed gold code with the next
title-ranked code in the same family, the note still contains the closed
sentence for the original rank, and the baseline reads those same closed
sentences (day-9 caveat stands). 33 of 50 cases are inapplicable because
their gold codes carry no ordinal rank (E11.9, I10, D50.9) - the injector
refuses to invent severity outside the N18/J45 title scales. wrong_code
stays deferred for lack of a verified mapping. Counts remain provisional
until the milestone 6 clinical review; they are a floor for the LLM
auditor to explain, not evidence the problem is solved.
