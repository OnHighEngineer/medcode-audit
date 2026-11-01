# Spec 018: cost/latency tracking at the transport boundary

## Purpose
Give every model call a price tag and a stopwatch. The spec-009 LLM
auditor already funnels every model call through one injected
`transport(prompt) -> reply_text`; wrapping that seam records what each
call costs (size) and how long it takes (clock) without touching the
auditor, the runner, or the frozen spec-005 run shape.

## Offline unit
Characters, not tokens: no tokenizer dependency, no provider-specific
accounting, exact and reproducible. Latency comes from an injected
`clock() -> number` (two readings per call, before and after); tests use
scripted clocks, real deployments would pass `time.monotonic`. No live
provider call is needed or made (Oct 21 rule).

## API
- `make_tracking_transport(transport, clock) -> (tracked, records)`:
  validates both are callable. `tracked(prompt)` behaves exactly like
  `transport(prompt)` but appends one record per call to `records` (a
  list the caller owns). It raises ValueError when the prompt is not a
  string, when a clock reading is not a number (bools excluded), when
  the clock goes backwards, or when the transport does not return a
  string - the failure surfaces on the offending call, in order.
- Record shape: `{call, prompt_chars, reply_chars, latency}` - `call`
  is 1-based in wrap order, chars are string lengths, latency is
  `end - start` in whatever unit the clock returns.
- `summarize_records(records) -> dict`: validates the list (each record
  a dict with `call` int >= 1, char counts int >= 0, latency
  number >= 0, bools excluded). Returns `{calls, total_latency,
  mean_latency, prompt_chars, reply_chars}`; `mean_latency` is None
  when there are no calls.
- `format_cost_latency(records) -> str`: deterministic plain text.
  Header line: `COST/LATENCY (PROVISIONAL): character counts and
  transport timings at the spec-009 boundary; synthetic accounting
  only, not trusted scores.` Then `calls N`; with zero calls
  `no calls recorded`, otherwise a latency line (total and mean) and a
  characters line (prompt in, reply out). No percentages.

## Placement
Records live beside the run, never inside it: the spec-005 run dict
keeps its frozen keys, and callers pass the records list to the summary
functions separately.

## Out of scope
Token counting, real provider pricing, wall-clock capture inside the
library (the caller injects the clock), persisting records, per-error-
type cost breakdowns (spec 017 strata already cover breakdowns).
