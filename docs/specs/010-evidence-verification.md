# Spec 010: evidence-span verification

## Contract
Module `medcode_audit/evidence.py`. Pure functions; no I/O.

`VERIFICATION_STATUSES = ('verified', 'unverified', 'invalid', 'not_applicable')`

### Span search
`find_span(note_text, quote) -> (start, end) | None`
- Both arguments must be strings and `quote` nonempty, else ValueError.
- Case-sensitive exact substring; returns character offsets `[start, end)`,
  or None when absent.

### Per-verdict verification
`verify_verdict(verdict, note_text) -> dict`
- `verdict` is a spec-007 verdict entry (dict with `code`, `verdict`, optional
  `evidence_quote`); `note_text` must be a string. Malformed inputs: ValueError.
- Policy:
  - SUPPORTED with a verbatim quote: `verified`, span recorded.
  - SUPPORTED without a quote: `unverified` (flagged, not an exception).
  - Any verdict whose quote is not verbatim: `invalid`.
  - Non-SUPPORTED without a quote: `not_applicable`.
- Record: `{'code', 'verdict', 'status', 'span'}` where `span` is the
  `(start, end)` tuple or None. Inputs are never mutated.

### Batch and summary
`verify_evidence(verdicts, note_text)` maps `verify_verdict` over a list of
verdict entries (list required, else ValueError), preserving order.
`verification_summary(records)` returns counts per status (every status key
present, zero-filled) plus `total`.

## Integration
`auditor_schema.validate_auditor_output` uses `find_span` for its verbatim
check - one rule, one implementation. Runner behavior is unchanged: an invalid
quote still fails closed there; `unverified` is a report-layer flag, not an
exception, so stub auditors without quotes keep working.

## Non-goals
Fuzzy matching, span rendering, report generation (item 22), changing the
runner's record shape or report format. All outputs stay provisional until the
milestone 6 review.
