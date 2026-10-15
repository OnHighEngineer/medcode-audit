# Spec 002: deterministic synthetic note generator

## Contract
`generate_cases(count=10, seed=0, start_id=4) -> list[dict]` returns JSON-ready
cases accepted by `parse_case`. Count is a nonnegative integer; seed is an integer;
start_id is a positive integer. Reject bools and other types with ValueError naming
the argument. Zero count returns an empty list. No global random state is changed.

IDs are gen-{number:03d}, increasing from start_id. The caller selects a nonoverlapping
range for later batches. Each record has synthetic=true, an explicit SYNTHETIC NOTE
prefix, one positive diagnosis with one verbatim evidence quote and injected_errors=[].
The closed vocabulary contains no names, MRNs, birth dates, contact details or dates.

## Coverage and reproducibility
Round-robin conditions: E11.9 (type 2 diabetes without complications), I10 (essential
hypertension), J45.30 (mild persistent asthma, uncomplicated), N18.31 (CKD stage 3a),
D50.9 (iron deficiency anemia, unspecified). Reuse the provisional day-1 mappings.
A batch of five covers all five. A local seeded RNG selects neutral note wrappers.
Same arguments reproduce identical output within this version. Different seeds may
coincide for a small batch; no distinctness promise. Returned dictionaries are independent.

## Publishing fixtures
Check in 10 generated cases, gen-004 through gen-013, with seed 42. Do not overwrite
syn-001 through syn-003. Store each in its own UTF-8 JSON file; validate the combined
directory using load_cases. Fixtures are provisional until the planned label review.

## Non-goals
Real patient data, LLM calls, official code lookup, clinical correctness claims,
error injection, negation/uncertainty or filesystem writing in the generator API.
