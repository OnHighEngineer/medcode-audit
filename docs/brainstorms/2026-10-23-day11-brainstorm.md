# Day 11 brainstorm: evidence-span verification

## Problem
Spec 007 already rejects a volunteered quote that is not verbatim in the note.
What is missing: one module that owns the verbatim rule, reports WHERE a quote
sits (span offsets for the later report generator), and states the policy for a
SUPPORTED verdict with no quote at all. Day 11 builds that verifier and points
the schema validator at it, so there is a single source of truth.

## Options considered

### SUPPORTED without a quote: hard failure or flagged
1. Hard failure in the runner. Rejected: frozen day-5/8 tests run stub auditors
   that return SUPPORTED with no quotes, and frozen tests do not change.
2. A verification status, not an exception. Chosen: `unverified` flags the
   verdict in the report layer; invalid quotes stay hard failures at the
   spec-007 boundary. Honest accounting without rewriting history.

### Status vocabulary
Closed set: `verified` (quote present and verbatim, span recorded),
`unverified` (SUPPORTED with no quote), `invalid` (quote not verbatim),
`not_applicable` (non-SUPPORTED with no quote). UNSUPPORTED and
WRONG_SPECIFICITY may carry a quote (e.g. the absent sentence); when they do it
is checked like any other.

### Wiring
1. Runner record shape changes. Rejected: frozen tests.
2. `auditor_schema` imports `find_span` from the new module. Chosen: one
   verbatim rule, one implementation; behavior unchanged, tests stay green.
   The analysis functions (`verify_evidence`, `verification_summary`) serve
   the day-12+ auditors and the item-22 report generator.

### Spans
`find_span` returns `(start, end)` character offsets, `None` when absent.
Offsets cost nothing now and save the report generator a re-scan later.

## Risks
A SUPPORTED verdict with no quote is now visibly `unverified` instead of
silently accepted; the baseline and the LLM prompt already require quotes, so
only stubs show up unverified. All outputs stay provisional.
