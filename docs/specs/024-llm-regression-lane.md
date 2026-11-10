# Spec 024: LLM-auditor lane for the regression suite

## Purpose
Day 26's regression suite guards the rule-baseline eval; the LLM
auditor's end-to-end behavior (prompt build, transport, reply parse,
spec-007 validation, runner integration) was guarded only by isolated
unit tests. This lane re-runs the same 50-case eval through
`make_llm_auditor` with a deterministic gold-truth canned transport and
snapshots the tally exactly like the baseline lane. Offline: canned
replies only, no provider, no spend. The guard covers WIRING - a
gold-truth reply set detects everything, so any drift in parsing or
validation shows up as a named mismatch. It does not re-validate labels
(milestone 6) and says nothing about real model quality.

## Gold-truth canned transport
`make_gold_transport(cases) -> transport` (new module canned_llm.py)

- `cases`: list of case dicts, else ValueError. Builds note_text ->
  {gold code: evidence_quote}. A repeated note_text is allowed only when
  its gold map is identical (the day-2 batch contains such template
  pairs); the same note with DIFFERENT gold raises ValueError - true
  ambiguity must fail loudly, never guess.
- The returned transport(prompt) extracts the note between the
  spec-009 `NOTE:\n"""` fences and the claimed codes from the
  `CLAIMED_CODES_JSON:` line. A prompt whose note matches no case, or
  whose claimed-codes JSON is unparseable, raises ValueError - fail
  closed, like the auditor it feeds.
- Reply: one JSON object; SUPPORTED with the case's committed verbatim
  evidence_quote for claimed codes in gold, UNSUPPORTED for the rest;
  missed_codes = sorted gold codes not claimed. Replies mirror real
  committed note content only - no invented mappings or new claims.

## Runner lane
`run_regression(cases, seeds=REGRESSION_SEEDS, lane='baseline')`

- `lane`: 'baseline' (default, byte-identical to day-26 behavior) or
  'llm'; anything else raises ValueError. The 'llm' lane evaluates with
  `make_llm_auditor(make_gold_transport(cases))`.
- Return shape is unchanged ({case_count, seeds: {...}}), so spec-022
  `check_snapshot` diffs either lane and every day-26/27 test passes
  untouched.

## Snapshot data
`data/regression/llm-snapshot.json` - the committed LLM-lane output,
same format and regeneration rules as the baseline snapshot.

## Out of scope
Real provider calls, imperfect/noisy canned replies (a later robustness
day if wanted), procedure vocabulary.
