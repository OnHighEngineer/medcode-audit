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
