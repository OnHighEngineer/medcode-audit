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

## Latest completed feature: day 7 (2026-10-19)
Week 1 review (plan item 7). 142 passing tests on Python 3.10.12 and on Python
3.11.16 (via uv) - the earlier 3.10-only caveat is closed. decision-log.md read
against flow.md and specs 001-006 with no drift. Week-1 review note at
docs/reviews/day-07-week-1-review.md; label review guide for the pending
milestone 6 human review at docs/reviews/label-review-guide.md. The provisional
gate is verified visible in README, flow.md, SESSION.md and the runner report.
Labels stay provisional until the human review is recorded. Next: read the
day-08 plan (week 2 starts: auditor output schema + validators). upcoding and
wrong_code stay deferred (no verified mapping source). One harmless pytest
iterator warning remains in a frozen day-3 test.
