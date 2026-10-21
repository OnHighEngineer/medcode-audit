# Spec 008: rule-based baseline auditor

## Contract
`medcode_audit/baseline.py` exposes `audit_baseline(note_text, claimed_codes)`,
an auditor callable for `run_eval` (spec 005) whose output always satisfies
spec 007.

- `note_text` must be a string and `claimed_codes` a list of strings, else
  ValueError. Inputs are never mutated. Same inputs, same output.
- The baseline knows only the five provisional mappings (code, condition
  phrase, stem) and the spec-003 closed sentences.

## Per-condition state (priority order)
1. affirmed: `Confirmed diagnosis: {phrase}.` is in the note.
2. negated: `Condition explicitly absent: {phrase}.` is in the note.
3. uncertain: `Possible diagnosis, not confirmed: {phrase}.` is in the note.
4. mentioned: the phrase or stem appears case-insensitively (prose notes).
5. absent: none of the above.

## Verdicts
- Known code, affirmed or mentioned: SUPPORTED. Evidence quote: the affirmed
  sentence, or the verbatim matched substring for a prose mention.
- Known code, negated: UNSUPPORTED with the absent sentence as evidence quote.
- Known code, uncertain or absent: UNSUPPORTED, no quote.
- Claimed code outside the five mappings: UNSUPPORTED, no quote (the baseline
  has no rule that could support it; documented limit).

## Missed codes
`missed_codes` lists, in table order, every known code whose condition is
affirmed or mentioned and which is not in `claimed_codes`.

## Known limits (state them wherever counts appear)
Lexical matching over five provisional conditions; the closed-sentence cases
were built from the same templates the baseline reads, so high detection there
is expected, not evidence of generalization. No general negation or paraphrase
handling. All counts stay provisional until the milestone 6 review.

## Non-goals
NLP, new code mappings, upcoding or wrong_code logic, LLM calls, scoring
policy. No changes to the injector, runner or gold data.
