# Day 2 brainstorm: reproducible synthetic notes

Templates or LLM-written notes? Templates: no API, no private data, exact evidence,
and repeatable runs. LLM-written notes add cost and label drift before a baseline exists.

Start with the five conditions already in the day-1 fixtures. Round-robin coverage
prevents small batches from accidentally missing a condition. Seed controls wording,
not labels or coverage. These are provisional labels, not coding advice.

Use IDs gen-004 onward, separate from syn-* hand-written fixtures. No names,
MRNs, birth dates, addresses or invented patient identifiers in note text. Each note
starts SYNTHETIC NOTE. Keep positive diagnoses only today; negation and uncertainty
need separate gold-label rules in day 3, not a random phrase that contradicts gold.
