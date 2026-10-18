# Session protocol (persistent memory across fresh sessions)

Each feature runs in a fresh session with no memory. The repo is the memory.

## Start of every session (in order, before touching code)
1. Read AGENTS.md (rules).
2. Read docs/plans/2026-10-13-30-day-plan.md and the latest docs/plans/*-day-NN-plan.md (what is next, what is done).
3. Read decision-log.md fully (what was chosen, why, what was rejected - do not re-propose rejected options without a new entry).
4. Read flow.md (current system and eval flow).
5. Read the relevant docs/specs/ file; run `pytest` to confirm the starting state is green.
6. State a one-paragraph summary of context and today's goal before starting.

## During the session
Spec first, failing tests next, then code. Never edit committed tests to make them pass.

## End of every session (required, before the final push)
1. Append decision-log.md entries (Chose / Why / Rejected) for every choice made.
2. Update flow.md to match the code.
3. Mark progress in the day plan and write the next day's plan file (docs/plans/YYYY-MM-DD-day-NN-plan.md) with open questions and handoff notes.
4. Run pytest, confirm green, commit as Manjunath S <manjuss0409@gmail.com>, push.

A session that skips the end steps leaves the next session blind. Treat it as not done.

## Latest completed feature: day 6 (2026-10-18)
Label validation prep `medcode_audit.review` (`sample_cases`, `build_review_sheet`,
`dump_sheet`, `load_sheet`, `summarize_review`, spec 006). 142 passing tests on
Python 3.10 in the sandbox (3.11 still unavailable; project target is 3.11). The
127 earlier tests are unchanged; 15 are new. Sampling is stratified round-robin
over the spec-003 sentence-marker strata; the sheet has one row per gold label
plus a control row per empty-gold case; the summary prints counts only. The
unmarked 12-case sample sheet (seed 42, two per stratum) is checked into
docs/reviews/day-06-label-review-sheet.json for the milestone 6 human review.
Next: read the day-07 plan (week 1 review). upcoding and wrong_code stay deferred
(no verified mapping source). One harmless pytest iterator warning remains in a
frozen day-3 test.
