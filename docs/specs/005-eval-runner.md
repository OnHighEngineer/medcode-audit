# Spec 005: eval runner skeleton

## Contract
`run_eval(cases, auditor, error_types=ERROR_TYPES, seed=0)` and
`format_report(run)` in `medcode_audit.runner`.

- `cases`: list of case dicts (same shape as `inject_error` input). Not a list: ValueError.
- `auditor`: callable `auditor(note_text, claimed_codes) -> dict`. Not callable: ValueError.
  It receives only the note string and a list of code strings. It never sees origins,
  injection or expected findings.
- `error_types`: iterable of known error types, else ValueError. `seed`: int, not bool,
  else ValueError. The same seed is used for every case.
- Cases are never mutated.

## Auditor output (validated, fail closed)
`{'verdicts': [{'code': str, 'verdict': one of VERDICTS}], 'missed_codes': [str]}`
- `VERDICTS = ('SUPPORTED', 'UNSUPPORTED', 'WRONG_SPECIFICITY', 'MISSED')`.
- `verdicts` must cover exactly the claimed codes, once each. Missing, extra or
  duplicate codes, an unknown verdict or any wrong type: ValueError.
- `missed_codes` must be a list of strings.

## Per-case result record
For each (case, error type) in input order:
`{source_case_id, error_type, seed, status, reason, expected_findings, false_flags}`
- `status`: `inapplicable` (injector said so; auditor is not called), `detected` or
  `not_detected`.
- `reason`: the injector's reason when inapplicable, else null.
- `false_flags`: gold-origin claimed codes the auditor did not mark SUPPORTED.
- Detection: missed -> code in `missed_codes`; unsupported and negated_claim -> that
  code is UNSUPPORTED. Detected only if every expected finding matches.

## Run result
`{'provisional': True, 'seed': seed, 'results': [...], 'tally': {...}}`.
`tally[error_type]` has `applicable`, `detected`, `not_detected`, `inapplicable`,
`false_flags` (total count) and `reasons` (reason -> count). Every requested error
type appears, even with zero cases.

## Report
Plain text, deterministic. First line states the numbers are provisional (synthetic
labels, no clinical review). One line per implemented error type with counts as
`detected k/n`, never percentages. Deferred types (reason `deferred_unverified_mapping`
for every case) print `not implemented` and the reason, no counts.

## Non-goals
Real auditor, CLI, metrics beyond counts, file output, new error mappings.
