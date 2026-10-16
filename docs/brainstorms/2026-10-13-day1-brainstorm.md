# Day 1 brainstorm: medcode-audit

## Problem
Medical coding errors lead to claim denials and compliance risk. Billing teams need a pre-submission check of claimed codes against chart evidence.

## Options considered
1. Code-assigning agent (coder). Rejected: crowded, hard to score, not the goal.
2. Auditor, provider side. CHOSEN.
3. Auditor, insurer side (payment integrity). Same engine, deferred; pitch only.

## Data
- Synthetic charts + codes first (labelled synthetic). No restricted data in git.
- MIMIC: gated (credentialing, training, DUA, zero-retention for external LLMs). Separate private track, only if access verified.
- Gold labels need validation before scores are trusted.

## Approach (design)
Pipeline: note + claimed codes -> auditor -> verdict + evidence quote per code -> evidence verifier -> report.
Eval harness injects known errors into gold cases and measures catch rate per error type.
Start with a rule baseline so the LLM auditor has something to beat.

## Open questions
- How big is the synthetic set before it stops being a toy (target 50, grow to 200)?
- Which ICD-10-CM code list source is license-safe to include?
- Is the LLM provider zero-retention if MIMIC track starts?

## Next
Write `docs/plans/2026-10-13-day-01-plan.md` and start feature 1 in a fresh session.
