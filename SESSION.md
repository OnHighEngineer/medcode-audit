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

## Latest completed feature: day 23 (2026-11-03)
Report generator, markdown v1 (spec 019, plan item 22 done). 328 passing
tests (316 carried + 12 new, all frozen) on Python 3.10.12 and 3.11.
`generate_report(run, analysis=None, cost_records=None)` assembles one
markdown eval report: it owns the title, provisional header and seed
line and embeds the frozen spec-005/017/018 formatters verbatim - it
assembles, never recomputes. HTML out of scope for v1. The 50-case
baseline report is docs/reviews/day-23-report.md (provisional).
wrong_code remains deferred. Next: read the day-24 plan. One harmless
pytest iterator warning remains in a frozen day-3 test.
