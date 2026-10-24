# Day 12 brainstorm: negation and uncertainty handling

## Problem
Two modules read assertion status today: the baseline (its private `_state`)
and, implicitly, every future auditor that must tell "confirmed" from "absent"
from "maybe". The logic should live in one detector with one documented policy,
over the five provisional conditions, saying plainly what it refuses to do.

## Options considered

### Status vocabulary
1. affirmed / negated / uncertain / absent only. Rejected: prose mentions are
   weaker than closed affirmed sentences, and collapsing them hides that.
2. Add `mentioned` (prose-only) and `conflict`. Chosen: six statuses, closed
   set. `mentioned` keeps prose honest; `conflict` surfaces contradictory
   closed sentences instead of silently picking a winner.

### Contradictions in one note
1. Priority rule (affirmed wins). Rejected: silently discards contradictory
   evidence, the same failure the day-3 goldset rejected.
2. Explicit `conflict` record listing every matched closed sentence. Chosen.
   The goldset never produces conflicts, so fixture behavior is unchanged; the
   baseline treats a conflict as UNSUPPORTED (no fabricated support).

### Prose negation
The day-1/2 prose notes are positive-only with non-vocabulary negations
("No chest pain"). General prose negation detection is NLP the project has
refused since day 3. The detector marks a prose mention `mentioned` and says
so; it does not guess negation in prose. Documented limit, not a gap.

### Reuse
Spans come from `evidence.find_span` (one verbatim rule). The baseline drops
its private `_state` and consults the detector; behavior on the fixtures is
identical, so the frozen tests stay green.

## Risks
A consumer could read `mentioned` as strong as `affirmed`; the spec orders the
statuses and the baseline's mapping shows the intended reading. All outputs
stay provisional until the milestone 6 review.
