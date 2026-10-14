# Spec 001: synthetic case schema and loader

## Purpose
Define what one eval case looks like and reject malformed cases before any auditor or metric touches them.

## Case (JSON object)
| field | type | rule |
|---|---|---|
| id | string | non-empty, unique within a data set |
| synthetic | boolean | must be exactly `true`; anything else (missing, false, "true") is rejected |
| note_text | string | non-empty clinical note, written by hand or generated, never real patient text |
| gold_codes | list of object | each has `code` and `evidence_quote` |
| injected_errors | list of string | each one of: wrong_code, upcoding, unsupported_code, missed_code, negated_condition. May be empty |

## gold_codes item
- `code`: ICD-10-CM shape, one letter, two digits, optional dot and 1-4 alphanumerics (e.g. E11.9, I10, J45.909). Shape only; no lookup in v1 (see decision-log).
- `evidence_quote`: non-empty and must appear verbatim in `note_text` (case-sensitive substring).

## Loader
- `parse_case(dict) -> Case` validates and returns a frozen dataclass.
- `load_case(path) -> Case` reads one JSON file.
- `load_cases(directory) -> list[Case]` loads every `*.json` in a directory, sorted by filename, and rejects duplicate ids.
- All failures raise `CaseValidationError` (a ValueError) with a message naming the field.

## Out of scope
Code description lookup, hierarchy checks, error injection logic, gold label validation (later plan items).
