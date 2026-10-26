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

## Latest completed feature: day 15 (2026-10-26)
ICD-10 code lookup tool (spec 012, plan item 15). 222 passing tests (201
frozen + 21 new) on Python 3.10.12 and 3.11.16. `code_lookup.py` answers
description, hierarchy and same-category family from a hand-checked 21-code
table (`icd10_table.py`, public ICD-10-CM titles, provenance noted); unknown
codes raise LookupError, bad shapes ValueError. No severity ordering, so
upcoding/wrong_code stay deferred. Manju's priority note from today: code
first, docs supporting. Next: read the day-16 plan (agent loop with tools,
plan item 16). One harmless pytest iterator warning remains in a frozen
day-3 test.
