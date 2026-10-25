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

## Latest completed feature: day 13 (2026-10-25)
Baseline vs LLM comparison recorded (docs/reviews/day-13-baseline-vs-llm.md).
201 passing tests unchanged on Python 3.10.12 and 3.11.16; no library code
added (light day). Three offline auditors compared over all 50 cases: the rule
baseline, a canned perfect-reader transport (identical counts - expected on
self-templated data, no live model claim), and a canned flag-everything
transport (48/48 "detected" beside 45 false flags, proving detection counts
are gameable and the false-flag column is the guard). Labels stay provisional
until the milestone 6 human review is recorded. Next: read the day-14 plan
(week 2 review). upcoding and wrong_code stay deferred (no verified mapping
source). One harmless pytest iterator warning remains in a frozen day-3 test.
