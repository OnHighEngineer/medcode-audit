# Day 20: failure analysis (provisional)

Command: `run_eval` over all 50 checked-in cases with
`make_mentioned_blind_auditor()` (spec 017: the spec-008 baseline rules
with mentioned-status evidence ignored), seed 0, all five error types,
then `format_failure_analysis(analyze_run(run, cases))`. Reproduce with
the same inputs; both are deterministic.

Runner counts under the weakened auditor:

```
PROVISIONAL: synthetic labels, no clinical review yet (milestone 6). Counts only, not trusted scores.
seed 0
wrong_code: not implemented (deferred_unverified_mapping), 50 cases skipped
upcoding: detected 17/17, not detected 0, inapplicable 33, false flags on gold claims 1
unsupported_code: detected 48/48, not detected 0, inapplicable 2, false flags on gold claims 15
missed_code: detected 25/38, not detected 13, inapplicable 12, false flags on gold claims 2
negated_condition: detected 16/16, not detected 0, inapplicable 34, false flags on gold claims 0
```

Failure analysis report:

```
FAILURE ANALYSIS (PROVISIONAL): synthetic labels, no clinical review yet (milestone 6). Explains where failures concentrate; counts only, not trusted scores.
seed 0

error type: wrong_code
not detected: none
false flags on gold claims: none
inapplicable: deferred_unverified_mapping 50

error type: upcoding
not detected: none
false flags on gold claims 1
  by stratum: none 1
  by condition band: multi_condition 1
  cases: syn-003 (D50.9)
inapplicable: no_ordinal_gold_code 33

error type: unsupported_code
not detected: none
false flags on gold claims 15
  by stratum: none 13
  by condition band: single_condition 11, multi_condition 2
  cases: gen-004 (E11.9), gen-005 (I10), gen-006 (J45.30), gen-007 (N18.31), gen-008 (D50.9), gen-009 (E11.9), gen-010 (I10), gen-011 (J45.30), gen-012 (N18.31), gen-013 (D50.9), syn-001 (E11.9, I10), syn-002 (J45.30), syn-003 (D50.9, N18.31)
inapplicable: no_unmentioned_condition 2

error type: missed_code
not detected 13
  by stratum: none 13
  by condition band: single_condition 11, multi_condition 2
  cases: gen-004, gen-005, gen-006, gen-007, gen-008, gen-009, gen-010, gen-011, gen-012, gen-013, syn-001, syn-002, syn-003
false flags on gold claims 2
  by stratum: none 2
  by condition band: multi_condition 2
  cases: syn-001 (I10), syn-003 (D50.9)
inapplicable: no_gold_code 12

error type: negated_condition
not detected: none
false flags on gold claims: none
inapplicable: no_negated_target 34
```

## Read this before the numbers
The weakened auditor's misses are fully explained by the stratum
breakdown: every one of the 13 missed_code failures and all 18 false
flags sits in the `none` marker stratum - free-text notes (the three
handwritten cases and the ten day-2 generated cases) where condition
evidence is only ever mentioned, never carried by a closed
affirmed/negated/uncertain sentence. An auditor that ignores
mentioned-status evidence is blind in exactly that stratum and nowhere
else. negated_condition is untouched because negation evidence is always
a closed marker. This is the intended demo shape, not a discovered
weakness of the real baseline: the spec-008 baseline reads mentioned
evidence and stays at 0 misses and 0 false flags on this set (day-9 and
day-19 reviews). Counts remain provisional until the milestone 6
clinical review.
