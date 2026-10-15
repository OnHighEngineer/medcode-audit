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
