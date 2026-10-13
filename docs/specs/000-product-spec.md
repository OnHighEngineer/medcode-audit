# Spec v1

## Problem
Coding errors (wrong code, upcoding, missed code, unsupported code) cause claim denials and audit risk. Billing teams need a check against the chart before submission.

## Users
Provider-side billing/coding review teams. (Same engine can later serve insurer payment-integrity checks.)

## Scope v1
- ICD-10-CM diagnosis codes, from synthetic notes.
- Input: note text + list of claimed codes.
- Output JSON: per-code verdict, evidence quote(s) from the note, reason; list of suggested missed codes.
- Eval harness: gold-labelled synthetic cases + injected error types; metrics per error type.

## Out of scope v1
CPT (v2, synthetic cases), real patient data, UI beyond a CLI/report, payer rules.

## Verdicts
SUPPORTED, UNSUPPORTED (no evidence), WRONG_SPECIFICITY, MISSED (added by auditor).

## Error injection types
wrong_code, upcoding, unsupported_code, missed_code, negated_condition (note says "no diabetes").

## Success criteria
- Eval harness runs with one command and prints a per-error-type report.
- Label validation step done before any score is trusted (see docs/plans/2026-10-13-30-day-plan.md).
- Baseline vs agent comparison reported.
