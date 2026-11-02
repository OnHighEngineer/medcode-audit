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

## Latest completed feature: day 22 (2026-11-02)
Week 3 review (plan item 21 done, docs-only day - no code or test
changes). 316 passing tests on Python 3.10.12 and 3.11, confirmed before
and after. docs/reviews/day-22-week-3-review.md covers the seven week-3
layers (specs 012-018), the consistency read (one drift fixed: day-15
flow section now cites spec 012), the deferred list (wrong_code mapping,
live LLM eval pending Manju's approval, milestone 6 label review) and
week 4's theme. Next: read the day-23 plan. One harmless pytest iterator
warning remains in a frozen day-3 test.
