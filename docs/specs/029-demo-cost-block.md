# Spec 029: demo cost block for the LLM lane

## Purpose
The spec-023 demo shows the baseline tally; the spec-028 cost snapshot
exists only as JSON. This spec lets one offline command also print the
llm lane's cost/latency summary, rendered by the spec-018 formatter, so
a reviewer sees the transport accounting without reading raw JSON.
Offline, canned transport, deterministic; numbers stay provisional
synthetic accounting.

## Rules
1. `format_cost_summary(summary) -> str` in cost_latency.py: renders a
   spec-018 summary dict (calls, total_latency, mean_latency,
   prompt_chars, reply_chars) with the same lines format_cost_latency
   produces. Validation mirrors summarize_records: the summary must be
   a dict with exactly those five keys; calls/prompt_chars/reply_chars
   ints >= 0 (not bool); total_latency a number >= 0; mean_latency a
   number >= 0, or None exactly when calls is 0. Anything else raises
   ValueError.
2. format_cost_latency delegates: format_cost_latency(records) ==
   format_cost_summary(summarize_records(records)). One rendering path;
   the existing frozen tests pin the output unchanged.
3. `run_demo_cost(case_dir=None, seed=DEMO_SEED) -> str` in demo.py:
   runs run_llm_cost for one seed on the committed cases and returns a
   context line (`llm lane (gold-truth canned transport), seed N`) plus
   the formatted summary. seed must be an int (bool rejected), case_dir
   must exist - same rules as run_demo.
4. `main(argv=None)`: with no arguments the output is byte-identical to
   today (the frozen test test_main_prints_exactly_run_demo pins it).
   `--cost` additionally prints the cost block after the report; any
   other argument raises ValueError.

## Non-goals
Changing the default demo output; baseline-lane cost (no transport);
real token or price accounting.
