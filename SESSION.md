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

## Latest completed feature: day 20 (2026-10-31)
Failure analysis report (spec 017, plan item 19 done). 300 passing tests
(287 carried + 13 new, all frozen) on Python 3.10.12 and 3.11.17.
`analyze_run(run, cases)` breaks not_detected rows and false flags down
by error type, spec-006 marker stratum and gold-count band;
`format_failure_analysis` renders deterministic provisional text with no
percentages. `make_mentioned_blind_auditor()` (demo-only, baseline rules
minus mentioned-status evidence) gives the report real failures: its
50-case run puts all 13 misses and all 18 false flags in the `none`
marker stratum (docs/reviews/day-20-failure-analysis.md, provisional).
wrong_code remains deferred. Next: read the day-21 plan. One harmless
pytest iterator warning remains in a frozen day-3 test.
