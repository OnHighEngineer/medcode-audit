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

## Latest completed feature: day 3 (2026-10-15)
50 provisional synthetic cases; 91 passing tests on Python 3.11.16. Read spec 003,
`docs/reviews/day-03-provenance.md` and day-04 plan before the next feature. Original
46 tests and 13 fixtures are unchanged. Negated/uncertain states are separate and
excluded from gold; all-nonpositive controls have empty gold. Independent clinical
review remains milestone 6. Day 4 is the error injector in a fresh feature session,
planned light cadence. Do not infer code hierarchy or mutate gold to represent a
claim. One harmless pytest iterator warning is recorded in the day-03 completion.
