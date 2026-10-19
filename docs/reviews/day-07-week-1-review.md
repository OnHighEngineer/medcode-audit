# Week 1 review (day 7, 2026-10-19)

## Suite state
142 tests passing on Python 3.10.12 and on Python 3.11.16 (via uv). The project
targets 3.11; both runs are green, so the earlier 3.10-only caveat is closed. One
harmless pytest iterator warning remains in a frozen day-3 test.

## What exists (plan items 1-6)
- Item 1-2: case schema and loader (`schema.py`, spec 001), synthetic note
  generator (`generator.py`, spec 002), 13 initial fixtures.
- Item 3: assertion gold set (`goldset.py`, spec 003), 37 scenarios, 50 cases
  total, affirmed-only gold with closed negated/uncertain sentences.
- Item 4: error injector (`injector.py`, spec 004), missed_code,
  unsupported_code, negated_condition; upcoding and wrong_code explicitly
  deferred (no verified mapping).
- Item 5: eval runner skeleton (`runner.py`, spec 005), pluggable auditor
  callable, fail-closed output validation, counts-only provisional report.
- Item 6: label validation prep (`review.py`, spec 006), stratified sampler,
  review sheet, agreement bookkeeping, unmarked 12-case sample sheet.

## What is deferred
- The milestone 6 human label review itself: prepared, not performed. Sheet and
  guide are ready (`day-06-label-review-sheet.json`, `label-review-guide.md`).
- Real auditors: only stubs exist; no auditor score is meaningful yet.
- upcoding and wrong_code: blocked on a verified, license-safe mapping source.
- CLI, percentages, CPT, payer rules.

## Provisional gate check
The gate is visible where a reader lands: README data policy and footer, flow.md
per-layer notes, SESSION.md status, the runner report's first line, and the
review module docs. No score is presented as trusted anywhere.

## Decision-log vs flow vs specs
Read through on day 7: every flow.md layer traces to a spec (001-006) and to
decision-log entries; no drift found. Deferred items match across the three.

## Risks for week 2 (auditor core)
- The runner's auditor interface is only exercised by stubs; the first real
  auditor may surface interface gaps. Keep the fail-closed validation.
- The injector's mention check is lexical over five provisional conditions; a
  keyword auditor can look good on it without generalizing. Say so in week-2
  reports.
- Label truth is provisional until the human review lands; week-2 eval numbers
  must keep the provisional header.
