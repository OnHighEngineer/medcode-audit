# Spec 007: auditor output schema and validators

## Contract
Module `medcode_audit.auditor_schema`. Pure validation; no I/O, no state.

Constant: `VERDICTS = ('SUPPORTED', 'UNSUPPORTED', 'WRONG_SPECIFICITY', 'MISSED')`.
The runner re-exports `VERDICTS` so existing imports keep working.

`validate_auditor_output(output, claimed_codes, note_text=None) -> dict`

- `output` must be a dict with `verdicts` (list) and `missed_codes` (list of
  strings). Anything else: ValueError.
- `claimed_codes` must be a list of strings, else ValueError.
- Each verdict is a dict with string `code` and `verdict` in `VERDICTS`. Codes
  cover exactly `claimed_codes`, once each. Unknown verdicts, duplicates,
  missing or extra codes: ValueError.
- A verdict may carry `evidence_quote`: then it must be a nonempty string, and
  when `note_text` is a string it must be a verbatim (case-sensitive) substring
  of it. With `note_text=None` no verbatim check runs. Violations: ValueError.
- Returns a normalized deep copy:
  `{'verdicts': [{'code', 'verdict', optional 'evidence_quote'}],
    'missed_codes': [...]}`. The input is never mutated; mutating the result
  does not affect the input.

## Runner integration
`run_eval` validates every auditor reply through this module and passes the
case note as `note_text`, so a volunteered evidence quote is checked against
the chart. Replies without quotes behave exactly as before. Detection matching,
false flags, tallies and the report are unchanged (spec 005).

## Non-goals
Evidence-span verification policy (item 11), span offsets, any auditor
implementation, new verdict names, payer rules. All outputs stay provisional
until the milestone 6 review is recorded.
