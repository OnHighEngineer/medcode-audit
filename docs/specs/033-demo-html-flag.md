# Spec 033: demo HTML output flag

## Purpose
run_demo_html (spec 025) renders the eval report as a standalone HTML
page, but it has no CLI path - a reviewer must call the API. This spec
adds one flag that prints it, keeping the markdown report the default
output. Offline, deterministic; counts stay provisional.

## Rules
1. `main(argv=None)`: `--html` prints run_demo_html() - the spec-025
   page with the spec-027 narrow-viewport rules, escaping and content
   unchanged - and nothing else.
2. `--html` is exclusive: combining it with `--cost` or
   `--cost-by-type` raises ValueError. The HTML page has no cost
   section, and appending the plain-text cost blocks would be neither
   valid HTML nor the frozen markdown output.
3. No-argument, `--cost` and `--cost-by-type` outputs stay
   byte-identical (the frozen tests pin all three). Any other argument
   raises ValueError.

## Non-goals
Adding cost blocks to the HTML page (the spec-025/027 rendering is
pinned); changing run_demo_html or render_html; a file-writing mode
(stdout only, like every demo flag).
