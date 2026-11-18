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

## Latest completed feature: day 36 (2026-11-18)
Snapshot self-check entry point (spec 032) + noisy-lane review
artifact. 419 passing tests (415 carried + 4 new, all frozen; no
existing test touched) on Python 3.10.12 and 3.11.
`python -m medcode_audit.regression` re-runs every lane - baseline,
llm, the three noisy lanes, the two cost lanes - and diffs each live
result against its committed snapshot via check_committed_snapshots ->
check_snapshot (the spec-022 diff, so the command and pytest can never
disagree), printing one OK/drift line per lane in SELF_CHECK_LANES
order with exit 0/1. Additive only; tests and implementation landed in
one same commit per the standing test-first rule. The review artifact
docs/reviews/day-36-noisy-lanes.md quotes the noisy snapshot verbatim:
wrong verdicts surface as 59 false flags per seed with every applicable
case still detected; fabricated quotes and dropped verdicts abort with
named validation errors on every seed. The procedure vocabulary branch
(items 23/24, spec 021 reserved) is ON HOLD awaiting an owner decision;
do not prep it. Next: read the day-37 plan.
