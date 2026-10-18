# Spec 006: label review prep (sampler, review sheet, agreement bookkeeping)

## Contract
Module `medcode_audit.review`. Pure functions over case dictionaries (the same
shape `inject_error` accepts). No file writes, no RNG, no clinical judgment:
nothing in the module suggests what a reviewer should mark.

Constants: `SHEET_NAME = 'medcode-audit-label-review'`, `SHEET_VERSION = 1`,
`MARKS = ('agree', 'disagree')`.

### Strata
`stratum_key(case)` reads the note and returns the presence letters of the closed
spec-003 sentence markers in fixed order: `A` for `Confirmed diagnosis:`, `N` for
`Condition explicitly absent:`, `U` for `Possible diagnosis, not confirmed:`.
A note with no marker returns `none`. Examples: `A`, `AN`, `AU`, `none`.

### Sampling
`sample_cases(cases, size, seed=0)` returns a new list of `size` case dicts.
- `cases` must be a list of dicts, each with a nonempty string `id` and a string
  `note_text`, with unique ids. Anything else: ValueError.
- `size` must be an int (not bool) with `1 <= size <= len(cases)`. `seed` must be
  an int (not bool). Violations: ValueError.
- Rule: group cases by stratum; order strata by key; within a stratum order cases
  by id and rotate by `seed % len(stratum)`. Take round-robin across strata in
  sorted order until `size` cases are picked. Same inputs, same output. Cases are
  never mutated.

### Review sheet
`build_review_sheet(cases)` validates `cases` as above and returns:
`{'sheet': SHEET_NAME, 'version': 1, 'provisional': True, 'rows': [...]}`.
One row per (case, gold code), in input case order then gold order:
`{'case_id', 'gold_code', 'evidence_quote', 'reviewer_mark': None,
'reviewer_note': ''}`. A case with empty gold contributes one control row with
`gold_code` and `evidence_quote` both None (the reviewer confirms nothing is
supported). Gold entries must be dicts with string `code` and `evidence_quote`,
else ValueError.

### Validation and round trip
`validate_sheet(sheet)` raises ValueError unless the sheet matches the format
exactly: correct name, version 1, `provisional` is True, and every row has exactly
the five keys with the right types; `reviewer_mark` is None or in `MARKS`;
`gold_code` is None exactly when `evidence_quote` is None. `dump_sheet(sheet)`
validates and returns canonical JSON (sorted keys, trailing newline).
`load_sheet(text)` parses a string and validates; any parse or format failure is
ValueError. `load_sheet(dump_sheet(sheet))` equals the input sheet.

### Agreement bookkeeping
`summarize_review(sheet)` validates, then returns counts only:
`{'total_rows', 'reviewed', 'unreviewed', 'agree', 'disagree', 'disagreements'}`,
where `disagreements` lists `{'case_id', 'gold_code', 'reviewer_note'}` for every
row marked `disagree`, in row order. No percentages, no scoring.

## Non-goals
Automated or LLM label review, fixture edits (those need a logged decision),
agreement statistics, auditor scoring, new error mappings. All labels stay
provisional until the human review is recorded.
