# Label review guide (milestone 6)

Short version: open the sheet, judge each row against its note, mark agree or
disagree. Until this review is recorded, every eval number stays provisional.

## What to open
- The sheet: `docs/reviews/day-06-label-review-sheet.json` (12 rows, one per gold
  label, two cases from each support stratum).
- The notes: `data/synthetic/<case_id>.json` holds the full note text for each
  `case_id` in the sheet.

## How to mark a row
For each row, read the case note and compare `gold_code` and `evidence_quote`:
- `agree`: the quote is verbatim in the note and clinically supports the code.
- `disagree`: anything is off (wrong code, quote does not support it, quote not
  verbatim). Write what is wrong in `reviewer_note`.
- Rows with `gold_code: null` are empty-gold controls: mark `agree` if no code is
  supported by the note, `disagree` if one should be there.

Leave `reviewer_mark` null for rows you skip. Do not edit `gold_code` or
`evidence_quote` in the sheet; the sheet is a record, not a fixture.

## After marking
Get the counts and the disagreement list:
```python
from medcode_audit.review import load_sheet, summarize_review
sheet = load_sheet(open('docs/reviews/day-06-label-review-sheet.json').read())
print(summarize_review(sheet))
```

## What happens to disagreements
Disagreements stay in the sheet as evidence. A fixture changes only through a
logged decision-log entry (what changed, why, which sheet rows motivated it).
The sheet is the evidence; the decision log is the authority.

## Extending the sample
The sample is deterministic: `sample_cases(all_cases, size, seed)`. The checked-in
sheet used `size=12, seed=42`. A larger sample (or a second seed) is a new sheet;
regenerate, never hand-pick cases.
