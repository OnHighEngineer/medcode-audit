# Spec 025: HTML rendering of the eval report

## Purpose
Render the spec-019 markdown report as one self-contained HTML page for
reviewers who will not read raw markdown. Plan item 22's HTML half,
deferred on day 23 and picked up now. Every number and quote still comes
from the frozen module formatters - this renderer translates the
assembled markdown, it never recomputes or re-renders values.

## API
`render_html(markdown) -> str`

- `markdown`: the spec-019 report text. Must be a string starting with
  `# `, else ValueError. The known report grammar only: one `# ` title,
  paragraph lines, `## ` section headings, fenced ``` code blocks.
  Anything outside that grammar (nested fences, headings deeper than
  h2, inline markdown like ** or [links]) is treated as literal text,
  never interpreted.
- Returns a complete `<!DOCTYPE html>` document: escaped `<h1>` title
  (also the `<title>`), the provisional header line in a prominent
  banner element, `<h2>` per section, `<pre><code>` per fenced block,
  `<p>` per paragraph line. One inline `<style>` block, no JavaScript,
  no external assets, no percentages. UTF-8 throughout; unicode passes
  through unescaped except the five HTML-significant characters.
- Deterministic for identical input.

## Escaping rules (the security core)
Every character of report text is untrusted: `&` `<` `>` `"` `'` are
escaped in ALL text nodes and attributes, including inside fenced
blocks and evidence quotes. An ampersand is escaped first so entities
can never double-decode. No part of the input may become markup.

## Out of scope
JavaScript interactivity, charts, styling frameworks, a markdown
library dependency, procedure vocabulary.
