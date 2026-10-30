# Spec 016: upcoding injection and scoring

Plan item 18, second half. Spec 015 built the ordinal upcoding detector;
this spec wires it in: the injector can inject a same-family higher-rank
code, the baseline flags it through that detector, and the runner scores it
with no new verdicts. wrong_code stays deferred.

## Supersedes
Spec 004 deferred upcoding because no hierarchy or same-family mapping was
verified ("none is invented"). The day-15 license-safe table plus the
spec-015 title-derived ranks now supply that verified mapping, so the
deferral lifts for ordinal families only. Three committed tests pinned the
deferral and change under AGENTS.md rule 2 (the spec's premise no longer
holds), each named in the day-19 decision-log entry:
- tests/test_error_injector.py::test_deferred_types_always_inapplicable
  (parametrization drops 'upcoding'; wrong_code keeps it)
- tests/test_error_injector.py::test_applicability_counts_over_37_assertion_cases
  (upcoding applicable becomes 11 of 37, from the scenario schedule)
- tests/test_eval_runner.py (the DEFERRED constant drops 'upcoding')
No other committed test changes; no assertion is weakened, and the new
contract is pinned by new frozen tests before the implementation lands.

## Injection (injector.py)
- Targets: gold codes with a rank (ordinal family) that have at least one
  same-category code with a strictly higher rank, in gold order. The seed
  picks the target: targets[seed % len(targets)].
- Replacement candidates: same-category table codes with a strictly higher
  rank, in table order; the seed picks candidates[seed % len(candidates)].
- The claimed list is the gold baseline with the target entry REPLACED in
  place by {'code': new_code, 'origin': 'injected'}; every other entry
  keeps origin 'gold'. Gold truth is never edited.
- injection: {'code': new_code, 'action': 'replaced',
  'replaced_code': target}.
- expected_findings: [{'code': new_code, 'finding': 'upcoding'}].
- Inapplicable reasons: 'no_ordinal_gold_code' (no ranked gold code),
  'no_higher_rank_in_family' (ranked gold already at the family's top
  rank). wrong_code keeps 'deferred_unverified_mapping'.

## Detection contract (runner unchanged)
An upcoding injection is detected when the auditor marks the injected code
UNSUPPORTED: the existing runner matching, no new verdicts, no auditor
output schema change. The note supports the family only at a lower rank,
so the higher-rank claim is unsupported by the note as written. The
spec-015 finding shape stays available to auditors as evidence; it is not
a second scoring path today.

## Baseline (baseline.py)
audit_baseline consults assess_upcoding first: a claimed code with an
upcoding finding is UNSUPPORTED with the finding's evidence_quote. Every
other code follows the day-8 status logic unchanged. Same-rank gold claims
cannot false-flag (equal rank never fires); negated, uncertain and absent
statuses never support a finding (spec 015).

## Report
upcoding prints ordinary counts (detected k/n, ...). wrong_code keeps the
'not implemented (deferred_unverified_mapping)' line. All counts stay
provisional and expected-not-a-result until the milestone 6 review.

## Non-goals
- No downcoding injection or flag (spec 015 note stands).
- No wrong_code mapping; it still needs a verified source.
- No new auditor-output keys; the LLM auditor and agent loop are
  untouched.
