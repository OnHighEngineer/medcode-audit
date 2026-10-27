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

## Latest completed feature: day 16 (2026-10-27)
Agent loop with tools (spec 013, plan item 16). 245 passing tests (222 frozen
+ 23 new) on Python 3.10.12 and 3.11.16. `agent_loop.py` runs a
one-JSON-object-per-turn loop over the spec-009 transport: the model may call
lookup_code, verify_quote or detect_assertions (local, deterministic, visible
in the transcript) before returning a spec-007-validated final answer.
Protocol violations raise ValueError, tool errors are observable, no final
within 8 steps raises RuntimeError. `make_agent_auditor` plugs into run_eval;
verified end to end over all 50 cases with a scripted transport. Offline
only. Next: read the day-17 plan (missed-code detection, plan item 17). One
harmless pytest iterator warning remains in a frozen day-3 test.
