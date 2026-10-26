# Week 2 review (day 14, 2026-10-26)

Suite: 201 passing on Python 3.10.12 and 3.11.16, unchanged this week except
additions that followed the test-first, green-remote rule. Every number below
stays provisional until the milestone 6 human label review is recorded.

## What exists after week 2
- Auditor output contract (day 8, spec 007): fail-closed validation, optional
  verbatim-checked evidence quotes, normalized copies.
- Rule baseline (day 9, spec 008): five provisional mappings + closed
  assertion sentences, verbatim quotes; perfect goldset detection recorded as
  expected, not a result (docs/reviews/day-09-baseline-eval.md).
- Offline LLM auditor v1 (day 10, spec 009): prompt builder, injected
  transport, fail-closed reply parsing. No network, SDK or credentials.
- Evidence-span verification (day 11, spec 010): closed four-status
  verification with span offsets; one verbatim implementation shared by gold
  data and auditors.
- Assertion-status detection (day 12, spec 011): six closed statuses
  including conflict; baseline rewired onto the shared detector.
- Baseline vs canned-LLM comparison (day 13): detection counts are gameable;
  the false-flag column is the guard.

## Consistency read (decision-log vs flow vs specs 007-011)
Every flow layer traces to a spec and to decision-log entries; the deferred
items match across all three documents. No drift found, no corrections needed.

## Deferred
- Live LLM eval: needs Manju's approval first - provider, secure secret
  intake, spend cap, data scope. The module cannot make a live call as built.
- upcoding and wrong_code mappings: still no verified hierarchy or
  same-family table; the injector keeps returning deferred_unverified_mapping.
- Milestone 6 human label review: sheet and guide are in docs/reviews; until
  it is recorded, every count in every report stays provisional.

## Risks for week 3 (agent and robustness)
- Code lookup (item 15) must stay license-safe: the day-2 open question about
  a redistributable ICD-10 description source is still open. Build the lookup
  over a small hand-checked table of the five provisional codes first; do not
  scrape or bundle a licensed code set.
- The agent loop (item 16) must keep the fail-closed stance: malformed tool
  replies raise, never count as detection.
- Cost/latency tracking (item 20) has no hook yet; the transport boundary is
  where it belongs. Do not add timing inside pure modules.
- Adding real description text for codes is new label content; it stays
  provisional and synthetic-safe like everything else.
