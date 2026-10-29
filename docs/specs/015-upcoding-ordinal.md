# Spec 015: upcoding detection for ordinal families

Plan item 18, narrowed. Upcoding = the claimed code's severity rank exceeds
the rank the note's evidence supports. Only families whose official ICD-10-CM
titles carry an ordinal scale are assessable; everything else is never
guessed.

## Ordinal source (cited, not invented)
The ranks come from the official code titles themselves (the day-15
license-safe table, public-domain ICD-10-CM titles):
- N18 (Chronic kidney disease): stage 1 < stage 2 (mild) < stage 3a <
  stage 3b < stage 4 (severe) < stage 5. N18.9 ("unspecified") has no rank.
- J45 (Asthma): mild intermittent < mild persistent < moderate persistent <
  severe persistent, all "uncomplicated".
E11, I10, D50 and D64 titles carry no ordinal scale: not assessable.

## Table change (icd10_table.py)
Entries for the ten ordinal codes gain a `rank` integer; every other entry
gains `rank: None`. The lookup API and all frozen spec-012 tests stand.

## API (medcode_audit/upcoding.py)
- `assess_upcoding(note_text, claimed_codes) -> list` of findings. A finding
  fires when ALL hold for a claimed code:
  1. the claimed code has a rank (ordinal family);
  2. the spec-011 detector reports an affirmed or mentioned condition in the
     same family (the supported code, always one of the five provisional
     mappings today);
  3. claimed rank > supported rank.
  Finding shape: `{code, supported_code, claimed_rank, supported_rank,
  evidence_quote, span}` with quote and span from the detector record.
- Negated, uncertain, absent and conflict statuses never support a finding.
- A claimed code at or below the supported rank, or with no rank, never
  fires. No downcoding flag today (separate question).
- Input checks match spec 009 (str note, list of str codes; else ValueError).
- Deterministic, offline, no state.

## Non-goals
- The injector's upcoding type stays deferred until day 19 wires this
  detector into a same-family injection.
- No severity judgment beyond title ranks; no prose severity NLP.
