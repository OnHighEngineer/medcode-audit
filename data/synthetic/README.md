# Synthetic fixtures

All cases here are synthetic and labelled `synthetic: true`. No real patient or Arintra data.

## Day-2 generated batch
`gen-004.json` through `gen-013.json`: generate_cases(10, seed=42, start_id=4).
Five conditions, two cases each; closed neutral wrappers, no patient identifiers.
The original syn-* fixtures are unchanged. Labels are provisional, not a validated
benchmark or coding advice. Regenerating another batch requires a fresh ID range.

## Day 3 assertion cases
37 fixed cases gen-014..050 bring the total to 50. `build_gold_cases(14)` in
`medcode_audit.goldset` reproduces them. Confirmed diagnoses enter gold with the
full sentence as evidence. Explicitly absent and possible/not-confirmed diagnoses
do not enter gold. Mixed notes and empty-gold controls are deliberate.

These are synthetic evidence-support rules, not payer coding rules. Mappings remain
provisional. Provenance, manifest and pending review checklist:
`docs/reviews/day-03-provenance.md`. Do not overwrite the old 13 fixtures.
