# Day 4 brainstorm: error injection

## Problem
The eval harness needs claimed-code lists with known, labelled errors. Gold truth
(`Case.gold_codes`) must never be edited to carry a claim.

## Options considered
1. Mutate `gold_codes` and record the change. Rejected: destroys the truth the
   auditor is scored against.
2. Add claimed codes to the case schema. Rejected today: frozen schema and 91 tests.
3. Separate result object holding the claimed list, built from an immutable case.
   Chosen.

## Which error types are grounded today
- missed_code: drop an affirmed gold code from the claim. Needs only the gold list.
- unsupported_code: claim one of the five known codes whose condition the note never
  mentions. Needs only the closed code table and a lexical mention check.
- negated_condition: claim a code whose condition the note states as explicitly
  absent, using the day-3 closed sentence. Needs only that sentence format.
- upcoding: needs a verified severity/specificity hierarchy. None is verified and no
  license-safe source was checked in. Deferred.
- wrong_code: its meaning (same-family wrong code) also needs a verified mapping.
  A swap of unrelated codes is just missed plus unsupported. Deferred.

## Determinism
No RNG. Candidates are listed in fixed order; an integer seed picks index
seed % len(candidates).

## Risks
Lexical mention checks only fit the closed vocabulary of the five mappings. They are
not an NLP negation or mention detector.
