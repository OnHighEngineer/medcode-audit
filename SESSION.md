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

## Latest completed feature: day 5 (2026-10-17)
Eval runner skeleton `medcode_audit.runner` (`run_eval`, `format_report`, `VERDICTS`,
spec 005). 127 passing tests on Python 3.10 in the sandbox (3.11 was not available
this session; project target is 3.11). The 110 earlier tests are unchanged; 17 are new.
The auditor is a plain callable seeing only note text and claimed codes; output is
validated fail closed; the report is provisional and prints counts only. Only stub
auditors exist. upcoding and wrong_code stay deferred (no verified mapping source).
Next: read the day-06 plan. Independent clinical label review is milestone 6; no
trusted scores until then. One harmless pytest iterator warning remains in a frozen
day-3 test.
