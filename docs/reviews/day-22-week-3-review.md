# Week 3 review (day 22, 2026-11-02)

Suite: 316 passing on Python 3.10.12 and 3.11, unchanged this week except
additions that followed the test-first, green-remote rule. Every number below
stays provisional until the milestone 6 human label review is recorded.

## What exists after week 3
- Code lookup (day 15, spec 012): shape-checking lookup over a hand-checked
  21-code ICD-10-CM table built from public titles; hierarchy and family,
  no severity ordering. This ended the day-4 deferral with a verifiable
  source.
- Agent loop (day 16, spec 013): one JSON object per turn over the spec-009
  transport; local deterministic tools (lookup_code, verify_quote,
  detect_assertions); fail-closed protocol; plugs into run_eval.
- Missed-code detection (day 17, spec 014): affirmed/mentioned conditions no
  claim covers, with verbatim evidence; validator contract unchanged.
- Upcoding detection (day 18, spec 015): title-derived ordinal ranks for
  N18 and J45 only; read-only assessment over the spec-011 detector.
- Upcoding injection and scoring (day 19, spec 016): injector replaces an
  ordinal gold with a seeded higher rank; scored by the existing UNSUPPORTED
  match, no new verdicts. 50-case eval: 17/17 detected, 0 false flags
  (docs/reviews/day-19-upcoding-eval.md, template-flattered as noted there).
- Failure analysis (day 20, spec 017): not_detected rows and false flags
  broken down by error type, spec-006 marker stratum and gold-count band;
  the weakened-auditor demo's failures land entirely in the stratum its
  blindness predicts (docs/reviews/day-20-failure-analysis.md).
- Cost/latency tracking (day 21, spec 018): every transport call accounted
  in characters plus injected-clock latency; records live beside the frozen
  spec-005 run shape; 119 calls tracked on the 50-case canned run
  (docs/reviews/day-21-cost-latency.md).

## Consistency read (decision-log vs flow.md vs specs 012-018)
Every week-3 layer traces to a spec and to decision-log entries. One drift
found and corrected today: the day-15 flow section did not cite spec 012
(days 16-21 cite theirs inline); the citation is added in this commit and
logged. The deferred list matches across all three documents. No other
corrections needed.

## Deferred
- wrong_code mapping: still no verified source; the injector refuses it by
  name (deferred_unverified_mapping). Needs a verifiable mapping or stays
  out.
- Live LLM eval: needs Manju's approval first - provider, secure secret
  intake, spend cap, data scope. All LLM paths stay canned and offline.
- Milestone 6 label review: every eval count in every review doc is
  provisional until the human review is recorded.

## Next week (week 4 of the 30-day plan)
Report generator (item 22), CPT synthetic cases (23), CPT auditing (24),
private MIMIC track only if credentialed and only in a separate private
repo/env with zero-retention LLM (25 - nothing in this repo), regression
suite + CI (26), demo script and README results (27), interview write-up
(28), polish (29), buffer/final release (30). The report generator must
render the standing conventions: provisional wording and no percentages.
