# Spec 017: failure analysis report

## Purpose
Turn a run result's failures into an explainable breakdown. A single
"not detected 3" count hides where a weak auditor fails; this module
groups not_detected rows and false flags by error type and case stratum
so the failure mode is visible. Reporting only: no scoring changes, no
clinical judgment.

## Inputs
- `run`: the dict returned by `run_eval` (spec 005), with `seed`,
  `results` (one row per case x error type) and `tally`.
- `cases`: the same case dicts the run was built from; every
  `source_case_id` in the run must resolve to exactly one case.

## Strata
Two independent groupings, both deterministic:
- **Marker stratum**: the spec-006 `stratum_key` over the source case's
  note text - the affirmed (A) / negated (N) / uncertain (U) closed-marker
  mix, or `none`. Reused as-is; no new text parsing.
- **Condition band** from the source case's gold code count:
  `no_gold` (0), `single_condition` (1), `multi_condition` (2 or more).

## API
- `condition_band(case) -> str`: one of the three bands above. Raises
  ValueError on a non-dict case or a missing/non-list `gold_codes`.
- `analyze_run(run, cases) -> dict`: validates both inputs (run is a
  dict with a list `results`; cases follow the spec-006 checks; every
  result row resolves to a case). Returns
  `{provisional: True, seed, error_types, not_detected, false_flags,
  inapplicable}` where `error_types` preserves the run's tally order and:
  - `not_detected[etype]`: `{total, by_stratum, by_band, cases}` -
    counts plus the sorted case ids with status `not_detected`.
  - `false_flags[etype]`: `{total, by_stratum, by_band, cases}` -
    `total` counts flagged gold codes (runner semantics); the stratum and
    band breakdowns count rows; `cases` is sorted
    `{case_id, codes}` pairs with codes sorted.
  - `inapplicable[etype]`: `{reason: count}` from the rows.
- `format_failure_analysis(analysis) -> str`: deterministic plain text.
  Every error type gets a section even when empty (`none`). Ordering is
  fixed: tally order for error types, sorted keys for strata and reasons,
  band order `no_gold`, `single_condition`, `multi_condition`, sorted
  case ids and codes. No percentages anywhere.

## Wording
Header line: `FAILURE ANALYSIS (PROVISIONAL): synthetic labels, no
clinical review yet (milestone 6). Explains where failures concentrate;
counts only, not trusted scores.` Counts stay provisional like every
other eval number.

## Demo weakened auditor
`make_mentioned_blind_auditor()` returns a canned, offline auditor that
follows the spec-008 baseline rules but ignores mentioned-status
evidence: mentioned gold reads as UNSUPPORTED (false flags) and missed
mentioned codes go unreported (misses). It exists only to give the
report real failures to analyze; it is not an auditor candidate.

## Out of scope
Percentages, significance testing, per-finding diffs, HTML output, any
live provider call.
