# Spec 020: case schema v2 - optional procedure codes

## Purpose
Let a synthetic case carry procedure claims alongside diagnoses, so the
eval can grow past ICD-10-CM-only auditing. This spec is deliberately
vocabulary-neutral: it defines shape and evidence rules only. Which real
or placeholder procedure vocabulary the case DATA uses is a separate
decision (pending the owner; see decision-log) - this spec commits no
real codes and no descriptions.

## v2 case addition
One new OPTIONAL field on the spec-001 case:

| field | type | rule |
|---|---|---|
| procedure_codes | list of object | each has `code` and `evidence_quote`; may be empty; ABSENT means a v1 case and parses unchanged |

## procedure_codes item
- `code`: string matching the generic shape `^[A-Z0-9]{4,7}$` -
  uppercase alphanumeric, 4 to 7 chars. This fits CPT-style (5 digits),
  HCPCS-Level-II-style (letter + 4 digits) and clearly synthetic
  placeholders alike, and bakes in no vocabulary.
- `evidence_quote`: non-empty, must appear verbatim in `note_text`
  (case-sensitive substring), same rule as gold_codes.

## Schema and loader behavior
- `parse_case` accepts the optional field and returns a Case whose
  `procedure_codes` is the validated list (empty when absent). Every v1
  case parses byte-identically to before; every v1 validation error is
  unchanged.
- The Case dataclass gains `procedure_codes` with a default empty list,
  so existing positional construction is unaffected.
- Malformed entries raise CaseValidationError naming the field:
  non-list, non-object items, missing/non-string/shape-violating code,
  missing/empty quote, quote not found in the note.

## Out of scope
Any real procedure vocabulary, code descriptions, lookup tables, case
data using real codes, and procedure auditing (plan item 24). The
runner and every existing auditor ignore procedure_codes in v2.
