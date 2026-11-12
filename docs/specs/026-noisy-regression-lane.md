# Spec 026: noisy canned-reply lanes (fail-closed robustness)

## Purpose
The llm lane (spec 024) answers from gold truth and detects everything;
nothing pinned how the validation layer behaves when replies are WRONG.
These lanes inject one deterministic corruption per reply and snapshot
the outcome: wrong-verdict replies flow through validation and surface
as false flags; fabricated-quote and dropped-verdict replies are
REJECTED by spec-007 validation, aborting the eval with a named
ValueError. The snapshot pins both halves of fail-closed behavior.
Offline, no provider, no spend. Guards validation wiring only; says
nothing about real model behavior. Counts stay provisional.

## Corruptions (canned_llm.make_noisy_transport(cases, corruption))
Built on the spec-024 gold transport parsing. `corruption` is one of:
- `wrong_verdict`: the first claimed code that IS in the case's gold is
  flipped to UNSUPPORTED with no quote. No gold code claimed -> clean
  reply. Passes validation; shows up as false flags on gold claims.
- `fabricated_quote`: the first SUPPORTED verdict's evidence_quote is
  replaced with 'FABRICATED QUOTE NOT IN NOTE'. No SUPPORTED verdict ->
  clean reply. Spec-007 validation rejects it (not a verbatim
  substring).
- `dropped_verdict`: the first verdict entry is omitted. Empty verdict
  list -> clean reply. Spec-007 validation rejects it (coverage).
Anything else raises ValueError.

## Runner lanes
LANES gains 'noisy_wrong_verdict', 'noisy_fabricated_quote',
'noisy_dropped_verdict'. For a noisy lane, each seed's run is wrapped:
a ValueError from the auditor is recorded as
`{'validation_error': <message>}` for that seed (the eval fails closed
on the first corrupt reply); a clean run records the usual per-error
tally. Existing lanes are byte-identical.

## Snapshot data
`data/regression/noisy-snapshot.json` = {'lanes': {lane: snapshot}} for
the three noisy lanes, same regeneration rules as the other snapshots.

## Out of scope
Statistical noise models, provider anything, procedure vocabulary.
