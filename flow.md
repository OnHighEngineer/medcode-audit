# Flow

## System flow (v1 target)
note + claimed codes -> parse/normalize -> auditor (rules baseline | LLM agent) -> per-code verdicts + evidence spans -> evidence verifier (quote must exist in note) -> report

## Eval flow
synthetic gold cases -> error injector -> auditor -> compare verdicts to injected-error truth -> metrics per error type -> report


## Data layer (day 1)
data/synthetic/*.json -> `load_cases()` -> `parse_case()` validation (synthetic flag, code shape, evidence quote is a substring of the note, known error types) -> `Case` objects for the eval runner.
Everything downstream (injector, runner, auditor) only sees validated cases.

## Commit cadence
Heavy days (10+ commits) x 3-4, then light days (1-2 commits) x 1-2. Light-day work is batched into the next heavy day. Day 0 and day 1 are heavy. Planned: days 2-3 heavy, days 4-5 light (week 1 review on day 7 stays in the plan).

## Change log of flow
- Setup: initial flow defined.
- Day 1: added the data layer (schema + loader) and the cadence note.

## Synthetic generation (day 2)
`generate_cases(count, seed, start_id)` -> five round-robin positive conditions +
local seeded wrapper selection -> JSON-ready synthetic dictionaries -> parse_case
validation -> one file per case -> load_cases -> future injector/eval.
No LLM, real identifiers, global RNG mutation or file writes inside the generator.
The checked-in batch uses count=10, seed=42, start_id=4 (gen-004 to gen-013).
Together with syn-001 to syn-003 the directory holds 13 cases. All labels remain
provisional until the manual label-validation milestone; no scores claimed.
- Day 2: generator and reproducible fixtures added; positive-only vocabulary.

## Assertion gold layer (day 3)
Explicit `(code, status)` scenarios -> `make_assertion_case` -> closed status
sentences + affirmed-only full-sentence gold quotes -> `parse_case` validation.
`build_gold_cases(14)` emits 37 fixed scenarios gen-014..050, independently of the
frozen day-2 positive generator. Negated and uncertain are separate statuses, both
excluded from support labels. Duplicate/contradictory conditions are rejected.
The full directory is 50 cases after expansion; the labels remain provisional.
See docs/specs/003-assertion-gold-set.md and docs/reviews/day-03-provenance.md.
No auditor, metrics or payer policy is implemented by this assertion builder.

## Error injection layer (day 4)
Immutable case dict + error_type + int seed -> `inject_error` -> new dict with
`claimed_codes` (gold/injected origin), injection, expected findings, or an explicit
inapplicable reason. Gold is never mutated. missed_code, unsupported_code and
negated_condition are implemented; upcoding and wrong_code are deferred until a
verified mapping exists. Over gen-014..050: 25 missed, 35 unsupported, 16 negated
applicable. See docs/specs/004-error-injector.md. No auditor or scoring yet.
- Day 4: injector module added (light day).

## Eval runner layer (day 5)
cases + auditor callable -> `run_eval` -> per (case, error type): `inject_error` ->
auditor sees only note text and claimed code strings -> output validated (fail closed)
-> expected findings matched -> per-type tally (applicable, detected, not detected,
inapplicable with reasons, false flags on gold claims) -> `format_report`.
The report says provisional on its first line and prints counts only. upcoding and
wrong_code show as not implemented. Only stub auditors exist; no real auditor, CLI
or trusted score. See docs/specs/005-eval-runner.md.
- Day 5: runner module and report added (light day).

## Label review layer (day 6)
checked-in cases -> `sample_cases(cases, size, seed)` (stratified round-robin over
spec-003 sentence-marker strata) -> `build_review_sheet` (one row per gold label,
control row per empty-gold case) -> human reviewer marks agree/disagree per row ->
`summarize_review` (counts plus disagreement list) -> disagreements fixed only via
a logged decision-log entry. No clinical judgment is automated; labels stay
provisional until the review is recorded. See docs/specs/006-label-review-prep.md
and the unmarked sample sheet docs/reviews/day-06-label-review-sheet.json.
- Day 6: review prep module added (heavy day).
- Day 7: week 1 review recorded (docs/reviews/day-07-week-1-review.md). Suite
green on Python 3.10 and 3.11. Label review guide added
(docs/reviews/label-review-guide.md); labels stay provisional until the human
review is recorded.
