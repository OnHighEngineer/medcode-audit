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

## Latest completed feature: day 39 (2026-11-21)
Week-6 consistency read (no drift) + self-check --only filter (spec 035).
435 passing tests (425 carried + 10 new, all frozen; no existing test
touched) on Python 3.10.12 and 3.11. `python -m medcode_audit.regression
--only LANE` re-checks just the named lanes: only their evals run, one
OK/drift line per named lane in SELF_CHECK_LANES order, exit 0/1 scoped
to them. Unknown lane names, a bare --only and any other argument raise
ValueError; no arguments keeps the spec-032 nine-lane behavior
byte-for-byte (frozen day-36 tests untouched). check_committed_snapshots
gains the optional only parameter with the same validation. The week-6
read of decision-log vs flow.md vs specs 019-034 found no drift: every
week-6 flow layer cites a spec that exists, README snapshot names and
test count match, SESSION/plans current. Tests and implementation
landed in one same commit per the standing test-first rule. The
procedure vocabulary branch (items 23/24, spec 021 reserved) is ON HOLD
awaiting an owner decision; do not prep it.
Next: read the day-40 plan.
