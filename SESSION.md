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

## Latest completed feature: day 24 partial (2026-11-04)
Case schema v2, vocabulary-neutral slice only (spec 020, plan item 23
PARTIAL). 348 passing tests (328 carried + 20 new, all frozen; no
existing test touched) on Python 3.10.12 and 3.11. `parse_case` accepts
an optional `procedure_codes` field - generic shape rule, verbatim
evidence quotes, v1 cases unchanged. Licensing research (AMA, CMS, US
DOL primary sources) shows CPT content requires an AMA license while
HCPCS Level II is CMS-maintained and public domain unless otherwise
noted; the vocabulary decision for case data is PENDING Manju (raised
via main, morning of Nov 4). The CPT plan item is NOT complete: case
data, lookup and procedure auditing wait on that decision. Next: read
the day-25 plan. One harmless pytest iterator warning remains in a
frozen day-3 test.
