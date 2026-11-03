# Spec 019: report generator (markdown v1)

## Purpose
Assemble one markdown eval report from the artifacts that already exist:
the spec-005 run, the spec-017 failure analysis, and the spec-018
cost/latency records. One document a reviewer can read top to bottom,
instead of three separate outputs. HTML is out of scope for v1.

## API
`generate_report(run, analysis=None, cost_records=None) -> str`

- `run`: the spec-005 run dict (required). Must be a dict with an int
  `seed`, a list `results` and a dict `tally`; anything else raises
  ValueError.
- `analysis`: the dict returned by `analyze_run` for the same run, or
  None. When given, its `error_types` must be exactly the run's tally
  keys in order and its `seed` must equal the run's seed; mismatch
  raises ValueError.
- `cost_records`: the records list from a spec-018 tracking transport,
  or None. Validated through the spec-018 record rules.

## Output
Deterministic markdown for identical inputs:

```
# medcode-audit eval report

EVAL REPORT (PROVISIONAL): synthetic labels, no clinical review yet
(milestone 6). Counts only, not trusted scores.

seed <N>

## Runner summary
<fenced: format_report(run) verbatim>

## Failure analysis            (only when analysis is given)
<fenced: format_failure_analysis(analysis) verbatim>

## Cost/latency                (only when cost_records is given)
<fenced: format_cost_latency(cost_records) verbatim>
```

The generator owns the title, the provisional header and the seed line;
section bodies are the frozen module formatters embedded verbatim in
fenced code blocks, so wording lives in exactly one place per module.
No percentages anywhere. An empty cost_records list renders the honest
"no calls recorded" section (a rule baseline makes no transport calls).

## Out of scope
HTML output, percentages, charts, persistence, live provider calls,
re-rendering or rewording the module outputs.
