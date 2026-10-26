# Spec 012: ICD-10 code lookup tool

Plan item 15. Gives auditors and the week-3 agent loop a license-safe way to
ask: what is this code, what family is it in, how specific is it.

## Scope
A small, hand-checked table of ICD-10-CM codes: the five provisional codes
(E11.9, I10, J45.30, N18.31, D50.9) plus near relatives in the same
categories. NOT a full code set. Descriptions are the public ICD-10-CM code
titles; every table entry carries a provenance note (see icd10_table.py).

## API (medcode_audit/code_lookup.py)
- `lookup(code) -> dict`: normalized copy of the table entry:
  `{code, description, category, category_description, block, block_title,
  chapter, chapter_range, chapter_title, family}` where `family` is the
  sorted tuple of same-category codes present in the table.
- `is_known(code) -> bool`: True when `lookup` would succeed.
- `known_codes() -> tuple`: all table codes, sorted.
- `family(code) -> tuple`: same-category codes in the table, sorted.

## Fail closed
- Non-string input, or a string that fails the day-1 ICD-10 shape rule
  (letter, two digits, optional dot, 1-4 alphanumerics): `ValueError`.
- Valid shape but not in the table: `LookupError`. The tool never guesses a
  description, never fabricates hierarchy.
- Normalization before lookup: strip whitespace, upper-case. `e11.9` and
  `E11.9` are the same code.
- Returned dicts are fresh copies; mutating one cannot corrupt the table.

## Non-goals (logged in decision-log)
- No scraped or bundled full ICD-10-CM set (license question from day 2
  stays open).
- No severity ordering, no upcoding inference. The table records family
  membership only; any severity claim needs a verified source first.
- No network, no files, no state.
