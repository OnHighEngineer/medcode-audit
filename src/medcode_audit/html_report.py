"""HTML rendering of the spec-019 eval report. See docs/specs/025-html-report.md.

Translates the assembled markdown report into one self-contained HTML page.
Every number and quote comes from the frozen module formatters - this module
never recomputes values. All report text is untrusted and fully escaped; no
JavaScript, no external assets. Deterministic.
"""
from __future__ import annotations

_ESCAPES = (('&', '&amp;'), ('<', '&lt;'), ('>', '&gt;'),
            ('"', '&quot;'), ("'", '&#x27;'))

_STYLE = """<style>
body{font-family:system-ui,sans-serif;max-width:60em;margin:2em auto;padding:0 1em;color:#1a1a1a}
h1{font-size:1.4em}
h2{font-size:1.1em;border-bottom:1px solid #ddd;padding-bottom:.2em}
.banner{background:#fff8e1;border:1px solid #e0c060;padding:.6em .8em;font-weight:600}
pre{background:#f6f8fa;border:1px solid #ddd;padding:.8em;overflow-x:auto}
code{font-family:ui-monospace,monospace;font-size:.9em}
@media (max-width:40em){pre{white-space:pre-wrap;overflow-wrap:anywhere}}
</style>"""


def _escape(text):
    for raw, esc in _ESCAPES:
        text = text.replace(raw, esc)
    return text


def render_html(markdown) -> str:
    """Render a spec-019 report markdown string as a standalone HTML page."""
    if not isinstance(markdown, str):
        raise ValueError('markdown must be a string')
    lines = markdown.split('\n')
    if not lines or not lines[0].startswith('# '):
        raise ValueError('report must start with a # title')
    title = lines[0][2:].strip()
    body = []
    in_fence = False
    for line in lines[1:]:
        if line.startswith('```'):
            body.append('<pre><code>' if not in_fence else '</code></pre>')
            in_fence = not in_fence
            continue
        if in_fence:
            body.append(_escape(line))
            continue
        if not line.strip():
            continue
        if line.startswith('## '):
            body.append(f'<h2>{_escape(line[3:].strip())}</h2>')
        elif 'PROVISIONAL' in line:
            body.append(f'<p class="banner">{_escape(line)}</p>')
        else:
            body.append(f'<p>{_escape(line)}</p>')
    if in_fence:
        raise ValueError('unterminated fenced block')
    return ('<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f'<title>{_escape(title)}</title>\n{_STYLE}\n</head>\n<body>\n'
            f'<h1>{_escape(title)}</h1>\n' + '\n'.join(body) + '\n</body>\n</html>\n')
