# Synthetic fixtures

All cases here are synthetic and labelled `synthetic: true`. No real patient or Arintra data.

## Day-2 generated batch
`gen-004.json` through `gen-013.json`: generate_cases(10, seed=42, start_id=4).
Five conditions, two cases each; closed neutral wrappers, no patient identifiers.
The original syn-* fixtures are unchanged. Labels are provisional, not a validated
benchmark or coding advice. Regenerating another batch requires a fresh ID range.
