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
