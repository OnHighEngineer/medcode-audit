# Day 8 brainstorm: auditor output schema and validators

## Problem
Week 2 adds real auditors (rule baseline, then LLM). Today the only output
contract is the runner's inline `_check_output`: any auditor that talks to the
runner must satisfy checks nobody can import, read or test on their own. Two
auditors satisfying hidden inline checks "by accident" is how week 2 drifts.
Day 8 makes the contract a module: one checked shape, one validator, reusable by
the runner today and by auditors and the evidence verifier later.

## Options considered

### Where the contract lives
1. Keep it inline in the runner. Rejected: unimportable, untestable alone, and
   every new auditor re-derives it by trial and error.
2. A separate `auditor_schema` module, runner re-exports `VERDICTS`. Chosen:
   frozen day-5 tests import `VERDICTS` from the runner, so the runner keeps the
   name as a re-export; the definition moves to the module.

### Evidence spans now or later
1. Require an evidence quote on every verdict. Rejected: SUPPORTED by omission
   (a missed code) has no span, and item 11 owns span verification policy.
2. No evidence field at all. Rejected: the LLM auditor (item 10) must return
   quotes, so the shape needs the field before that work starts.
3. Optional `evidence_quote` per verdict, validated when present. Chosen: when
   present it must be a nonempty string, and when the caller passes the note it
   must be a verbatim substring - the same standard gold evidence is held to.
   The runner passes the note, so any auditor that volunteers a quote is checked
   against the chart today; item 11 builds the full verifier on this hook.

### Return value
1. Raise on invalid, return nothing. Rejected: callers immediately rebuild the
   code->verdict map; returning a normalized copy saves every caller the work.
2. Return a normalized deep copy. Chosen: the caller can mutate the result
   without touching the auditor's object, and validation of the copy is proof
   the shape is right.

## Risks
The runner now rejects volunteered bad quotes it used to ignore. No committed
auditor returns quotes, so no behavior changes today; the decision log records
the new strictness. MISSED stays a report field, not a per-claim verdict.
