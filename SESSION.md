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

## Latest completed feature: day 44 (2026-11-26)
README consistency pins (tests-only day). 463 passing tests (461 carried
+ 2 new, all frozen; no existing test touched) on Python 3.10.12 and
3.11.18. tests/test_readme_consistency.py pins two invariants the repo
already states: every non-empty line of the README's day-27 headline
block appears verbatim in docs/reviews/day-27-demo-output.md (flow.md's
"quotes its tally lines verbatim" claim), and every committed
data/regression/*.json filename is named in the README (the drift class
the week-5 read caught by hand). Both tests were proven sensitive
locally - a corrupted tally line or snapshot filename turns them red -
and the invariant holds, so no document or implementation changed. The
procedure vocabulary branch (items 23/24, spec 021 reserved) is ON HOLD
awaiting an owner decision; do not prep it.
Next: read the day-45 plan.
