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

## Latest completed feature: day 38 (2026-11-20)
Self-check doc-artifact lanes (spec 034) + stale artifact regenerated.
425 passing tests (422 carried + 3 new, all frozen; no existing test
touched) on Python 3.10.12 and 3.11. SELF_CHECK_LANES gains demo_report
and demo_html: run_demo() and run_demo_html() are pinned byte-exact
against the committed day-27/day-29 review artifacts, with drift
strings naming the file and first differing line. The morning check
found the day-29 HTML artifact stale since the intentional spec-027
narrow-viewport change (Nov 13) - exactly the drift class these lanes
catch - and regenerated it to the current rendering. The reviews
directory resolves from the repo with a reviews_dir override seam, so
the frozen spec-032 data_dir contract is untouched. Tests and
implementation landed in one same commit per the standing test-first
rule. The procedure vocabulary branch (items 23/24, spec 021 reserved)
is ON HOLD awaiting an owner decision; do not prep it.
Next: read the day-39 plan.
