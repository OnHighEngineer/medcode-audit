# Spec 004: deterministic error injector

## Contract
`inject_error(case, error_type, seed=0)` takes a case dictionary (same shape as
`parse_case` input) and returns a new JSON-ready dictionary. The case is never
mutated and its `gold_codes` and `injected_errors` are untouched. The result is
validated against the five known error types; unknown types raise ValueError. `seed`
must be an int and not a bool, else ValueError. `case` must be a dict, else ValueError.

Result keys:
- `source_case_id`: the case id.
- `error_type`: as requested.
- `seed`: as given.
- `applicable`: bool.
- `reason`: null when applicable, otherwise one closed reason string.
- `claimed_codes`: list of `{code, origin}` or null when inapplicable. `origin` is
  `gold` for codes copied from gold and `injected` for the added code.
- `injection`: null when inapplicable, else `{code, action}` with action `added` or
  `removed`.
- `expected_findings`: list of `{code, finding}`; finding is `missed`, `unsupported`
  or `negated_claim`. Empty when inapplicable.

Baseline claim = gold codes in order, origin `gold`.

## Transformations
- missed_code: needs at least one gold code. Candidates are gold codes in order; the
  seed picks one; it is removed from the claim. Finding: `missed`. Empty gold:
  reason `no_gold_code` (deleting from an empty claim proves nothing).
- unsupported_code: candidates are known codes (table order) not in gold whose
  condition is not mentioned. "Mentioned" means the note, lowercased, contains the
  condition phrase or its stem (diabet, hypertens, asthma, kidney, anemi). The seed
  picks one; it is appended. Finding: `unsupported`. None left: reason
  `no_unmentioned_condition`.
- negated_condition: candidates are known codes (table order) whose closed sentence
  `Condition explicitly absent: {condition}.` appears in the note and which are not
  in gold. The seed picks one; it is appended. Finding: `negated_claim`. Uncertain or
  merely absent conditions are not targets. None: reason `no_negated_target`.
- upcoding and wrong_code: always inapplicable, reason `deferred_unverified_mapping`.
  No hierarchy or same-family mapping is verified; none is invented.

## Non-goals
Auditor, scoring, payer rules, new code mappings, schema changes, writing files.
All results are provisional until the milestone 6 clinical review.
