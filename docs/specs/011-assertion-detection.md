# Spec 011: assertion-status detection (negation and uncertainty)

## Contract
Module `medcode_audit/assertions.py`. Pure functions over the five provisional
mappings; no NLP claims.

`ASSERTION_STATUSES = ('affirmed', 'negated', 'uncertain', 'mentioned',
'absent', 'conflict')`

`detect_assertions(note_text) -> list` of one record per known condition, in
table order. `note_text` must be a string, else ValueError.

`status_for(note_text, code) -> dict` returns the record for one known code;
an unknown code raises ValueError.

## Per-condition detection
Closed spec-003 sentences first: affirmed (`Confirmed diagnosis: {phrase}.`),
negated (`Condition explicitly absent: {phrase}.`), uncertain (`Possible
diagnosis, not confirmed: {phrase}.`).
- Exactly one kind matches: that status; the sentence is the record's `quote`
  and `span` (via `evidence.find_span`).
- Two or more kinds match: status `conflict`, `quote` and `span` are None, and
  `conflicting` lists every matched closed sentence in the order affirmed,
  negated, uncertain. The baseline treats `conflict` as UNSUPPORTED.
- No closed sentence: a case-insensitive phrase or stem match is `mentioned`,
  with the verbatim matched substring as `quote` and its span. Otherwise
  `absent` (`quote` None, `span` None).

Record: `{'code', 'status', 'quote', 'span'}` plus `conflicting` only when the
status is `conflict`. Inputs are never mutated; same note, same output.

## Known limits
Prose mentions are lexical: no general prose negation or paraphrase detection
(the fixtures' prose is positive-only by construction). The detector reads only
the five provisional conditions.

## Integration
The baseline consults `detect_assertions` instead of its private state logic;
mapping is unchanged (affirmed/mentioned SUPPORTED with quote, negated
UNSUPPORTED with the absent sentence, everything else UNSUPPORTED without a
quote, conflicts UNSUPPORTED). Existing behavior on all fixtures is identical.

## Non-goals
General negation/uncertainty NLP, new conditions, scoring changes, runner
changes. All outputs stay provisional until the milestone 6 review.
