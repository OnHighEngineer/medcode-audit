# Day 5 brainstorm: eval runner skeleton

## Problem
The injector produces claimed codes with known expected findings. Nothing yet checks
an auditor against them. The runner must connect cases, injector and a pluggable
auditor, and tally outcomes per error type, without building the real auditor.

## Options considered
1. Runner calls a concrete rule-based auditor. Rejected: week 2 work, and it would
   hide the interface behind one implementation.
2. Auditor as a plain callable `auditor(note_text, claimed_codes)`. Chosen. Tests use
   small stub auditors; later auditors plug in without runner changes.
3. Give the auditor the whole injected result. Rejected: it would leak the injection
   and expected findings, so a stub could "pass" by reading the answer.

## Verdict vocabulary
Spec 000 lists SUPPORTED, UNSUPPORTED, WRONG_SPECIFICITY, MISSED. They live in the
runner module as `VERDICTS`; WRONG_SPECIFICITY is accepted but no implemented error
type expects it yet. MISSED is not a per-claim verdict: missed codes come back in a
separate `missed_codes` list.

## Matching expected findings
- missed -> the removed code appears in `missed_codes`.
- unsupported -> the injected code gets UNSUPPORTED.
- negated_claim -> the injected code gets UNSUPPORTED (a negated condition has no
  support in the note).

## Reporting deferred types
upcoding and wrong_code are deferred. The report lists them as "not implemented" with
the injector's reason and shows no detection counts, so it never implies coverage.

## Risks
All labels are provisional until the milestone 6 review. The report says so on its
first line and prints counts, not percentages.
