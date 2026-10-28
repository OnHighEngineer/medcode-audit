# Spec 014: missed-code findings with evidence

Plan item 17. Missed-code detection becomes a first-class surface: not just
which codes no claim covers, but the verbatim evidence behind each finding.

## API (medcode_audit/missed.py)
- `find_missed(note_text, claimed_codes) -> list` of findings, one per
  supported-but-unclaimed condition:
  `{code, evidence_quote, span}` where quote and span come from the spec-011
  detector record. `span` is the (start, end) tuple from spec-010 find_span.
- A finding is emitted only for detector statuses `affirmed` or `mentioned`:
  conditions the note actually supports. `negated`, `uncertain`, `absent`
  and `conflict` never produce a missed finding.
- Input checks match spec 009: note_text must be str, claimed_codes a list
  of str; otherwise ValueError.
- Deterministic, offline, no state.

## Composition
- baseline.py derives its `missed_codes` from `find_missed` (one
  implementation; behavior on the fixtures is unchanged, frozen tests stand).
- agent_loop.py adds a fourth tool `find_missed` with args
  `{"claimed_codes": [...]}` returning `{"ok": true, "result": [<findings>]}`
  (spans serialized as [start, end] lists). This extends the spec-013 closed
  tool set; the fail-closed rules are unchanged (bad arg types raise
  ValueError, unknown tools raise ValueError).

## Non-goals
- The spec-007 auditor contract is unchanged: `missed_codes` stays a list of
  code strings. Evidence travels on the tool surface, not in the validator.
- No prose negation NLP, no new conditions, no severity ordering.
