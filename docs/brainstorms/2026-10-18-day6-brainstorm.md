# Day 6 brainstorm: label validation prep

## Problem
All gold labels are provisional. Before any auditor score is trusted (milestone 6),
a human has to review a sample of gold labels and record where they disagree.
Today there is no way to pick that sample reproducibly, no sheet to mark up, and
no bookkeeping for agreement. Day 6 builds those three things. It does not review
anything itself and never automates clinical judgment.

## Options considered

### Sampling rule
1. Random sample with `random.Random(seed)`. Rejected: shuffles are harder to
   hand-verify and review than an explicit order rule.
2. First-N cases. Rejected: the directory is ordered by construction batch, so
   first-N skips whole label patterns (negated, uncertain, empty-gold controls).
3. Stratified round-robin, chosen. Strata come from the closed day-3 assertion
   sentences, so every support pattern in the set is guaranteed a seat. Within a
   stratum the cases are sorted by id and rotated by the seed, exactly the
   deterministic style the injector already uses.

### Strata definition
1. Parse gold provenance metadata. Rejected: cases carry no status fields; adding
   them is a schema change with its own spec.
2. Derive strata from the three closed sentence markers (affirmed, negated,
   uncertain). Chosen: the markers are part of spec 003, so the strata are
   inspectable and stable. Prose notes without any marker (the day-1/2 cases)
   form the `none` stratum, which keeps them in the sample.

### Review sheet format
1. One row per case with a list of codes. Rejected: a reviewer cannot mark one
   code wrong and another right without splitting the row afterwards.
2. One row per (case, gold code), plus one control row per empty-gold case.
   Chosen: each label gets its own agree/disagree mark and note. The control row
   asks the reviewer to confirm that no code is supported, which is also a label.
3. Spreadsheet/CSV. Rejected: JSON round-trips losslessly through the repo and
   validates with the same strictness as the other artifacts.

### Agreement record
1. Percentages and a kappa statistic. Rejected: the set is small and the counts
   are the auditable artifact; rates get computed by the human reviewer later.
2. Counts plus an explicit disagreement list. Chosen: `summarize_review` reports
   total, reviewed, unreviewed, agree, disagree and the disagreement rows.

### Where disagreements go
Disagreements stay in the sheet rows. A fixture changes only through a logged
decision-log entry, so the sheet is the evidence and the log is the authority.

## Risks
The strata reflect sentence templates, not clinical difficulty. A stratum with a
systematically wrong template will still be caught, because every stratum is
sampled. All outputs stay provisional until the human review is recorded.
