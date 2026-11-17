# Spec 031: demo per-error-type cost block for the LLM lane

## Purpose
Spec 030 splits the llm lane's cost accounting per error type, but the
split exists only as JSON. Like spec 029 did for the combined totals,
this spec lets one offline command print one spec-018 summary block per
error type, rendered by the spec-029 formatter and sourced from
run_llm_cost_by_type, so a reviewer sees where the transport volume
concentrates without reading raw JSON. Offline, canned transport,
deterministic; numbers stay provisional synthetic accounting.

## Rules
1. `run_demo_cost_by_type(case_dir=None, seed=DEMO_SEED) -> str` in
   demo.py: runs run_llm_cost_by_type for one seed on the committed
   cases and returns a context line
   (`llm lane (gold-truth canned transport), seed N, by error type`)
   plus, per error type in schema.ERROR_TYPES order, the type name on
   its own line followed by its format_cost_summary block. seed must be
   an int (bool rejected), case_dir must exist - same rules as run_demo
   and run_demo_cost.
2. One rendering path: every block comes from format_cost_summary; the
   by-type view adds no formatting of its own.
3. `main(argv=None)`: with no arguments and with `--cost` alone the
   output is byte-identical to today (the frozen tests pin both).
   `--cost-by-type` additionally prints the per-type blocks after the
   report (after the `--cost` block when both flags are given). Any
   other argument raises ValueError.

## Non-goals
Changing the default or `--cost` demo output; per-type cost on the
baseline or noisy lanes (spec 030 already scopes those out); real token
or price accounting.
