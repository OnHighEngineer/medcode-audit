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

## Latest completed feature: day 46 (2026-11-28)
Repo metadata + README import pins (tests-only day). 475 passing tests
(471 carried + 4 new, all frozen; no existing test touched) on Python
3.10.12 and 3.11.18. tests/test_repo_metadata.py pins: requires-python
matching the CI matrix (the 2026-11-14 by-hand fix), CI running pytest
on push/PR to main, pyproject pointing pytest at src/ and tests/ (the
README's run-from-root instruction), and every `from medcode_audit...`
import name in the README snippets still existing. Each pin was proven
sensitive locally (a bumped floor or a misspelled README import goes
red, then green after restore); all four hold, so no document or
implementation changed. The procedure vocabulary branch (items 23/24,
spec 021 reserved) is ON HOLD awaiting an owner decision; do not prep
it.
Next: read the day-47 plan.
