# Spec 040: label review summary command

Status: implemented (day 45, 2026-11-27).

## Problem
Milestone 6 is the human label review: a reviewer marks a spec-006
sheet (agree/disagree per row), then the agreement is tallied.
summarize_review does the tally, but only as a library call - the
reviewer, who is not necessarily running pytest or writing Python, has
no offline command that turns a marked sheet into the summary the
decision log needs. No clinical judgment is involved in this step:
the human marks, the tool counts.

## Contract
`python -m medcode_audit.review SHEET.json`

- Exactly one argument, the path to a marked review sheet; anything
  else (no argument, extra arguments, flags) raises ValueError.
- The sheet text is loaded with the spec-006 load_sheet, so every
  spec-006 validation rule applies unchanged; a missing file, unreadable
  path, invalid JSON or invalid sheet raises ValueError.
- On success it prints format_review_summary(summarize_review(sheet))
  and exits 0. Unreviewed rows are reported, not an error: a partially
  marked sheet summarizes the marks present.

`format_review_summary(summary) -> str` in review.py:

- Validates its input the way format_cost_summary does (spec 029):
  summary must be a dict with exactly the six spec-006 keys; the five
  counts must be ints >= 0 (not bool); disagreements must be a list of
  dicts with exactly the keys case_id, gold_code, reviewer_note
  (case_id and reviewer_note strings, gold_code a string or None).
  Anything else raises ValueError.
- Deterministic plain text in the house style: a provisional header
  line, the five counts one per line, then the disagreement list in
  input order, one line each as `- <case_id> [<gold_code>] <note>`,
  with a None gold_code (a control row) rendered as `control` and an
  empty note omitted. No percentages.

## Non-goals
- Sampling or building a sheet from the command (spec 006's library
  covers prep; the committed day-06 sheet stays the canonical sample).
- Marking or editing rows (the human reviewer owns every mark).
- Resolving disagreements (decision-log rule: fixes come only from a
  logged entry, never from a tool).
