# Spec 003: explicit assertion policy and 50-case synthetic set

## Contract
`make_assertion_case(case_id, assertions)` accepts a nonempty string ID and a list
of `(code, status)` pairs. Codes belong to the five day-2 mappings. Status is exactly
`affirmed`, `negated` or `uncertain`. Reject malformed pairs, unknown codes/statuses
and duplicate conditions (including contradictory statuses) with ValueError.
Empty assertions are rejected. Inputs are not mutated; output is JSON-ready.

Every note begins `SYNTHETIC NOTE. Assertion exercise.`. Sentences are:
- affirmed: `Confirmed diagnosis: {condition}.`
- negated: `Condition explicitly absent: {condition}.`
- uncertain: `Possible diagnosis, not confirmed: {condition}.`

Only affirmed conditions enter gold_codes, with the entire affirmed sentence as
verbatim evidence. Negative/uncertain conditions never enter gold, even in mixed
notes. Order follows input order. Empty gold lists are valid for nonpositive notes.
No injected errors yet. This labels evidence support, not payer coding rules.
No free-text patient fields or arbitrary text generation. IDs are dataset keys.

## Batch
`build_gold_cases(start_id=14)` returns 37 deterministic, independent dictionaries.
Reject noninteger, boolean or nonpositive start_id. IDs are gen-014..050 by default.
The scenario schedule uses five single affirmed, five single negated, five single
uncertain, ten affirmed/negated pairs (next and second-next conditions), five
 affirmed/uncertain pairs, five adjacent affirmed pairs and two all-negated/all-
uncertain notes. All 37 notes are distinct. No seed or global RNG access.

The old 13 fixtures remain byte-for-byte unchanged. Combined load_cases count is
50. All labels stay provisional. Record batch provenance and a sample-review
checklist outside the fixture JSON directory. No clinical accuracy scores today.

## Non-goals
NLP negation detection, payer rules, code table validation, real data, new mappings,
error injection and auditor implementation. Do not change day-1/2 tests or APIs.
