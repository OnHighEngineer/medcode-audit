from pathlib import Path

import pytest

from medcode_audit.demo import run_demo, run_demo_html
from medcode_audit.html_report import render_html

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / 'data' / 'synthetic'

REPORT = run_demo(CASES)


def test_validation():
    with pytest.raises(ValueError):
        render_html(42)
    with pytest.raises(ValueError):
        render_html('no title here')
    with pytest.raises(ValueError):
        render_html('## section first')


def test_document_shape_and_safety():
    html = render_html(REPORT)
    assert html.startswith('<!DOCTYPE html>')
    assert '<h1>medcode-audit eval report</h1>' in html
    assert '<title>medcode-audit eval report</title>' in html
    assert '<h2>Runner summary</h2>' in html
    assert '<h2>Failure analysis</h2>' in html
    assert '<pre><code>' in html and '</code></pre>' in html
    assert 'PROVISIONAL' in html
    assert '<script' not in html.lower()
    assert 'http://' not in html and 'https://' not in html
    assert '%' not in html


def test_provisional_header_is_a_banner():
    html = render_html(REPORT)
    banner = [l for l in html.splitlines() if 'PROVISIONAL' in l and 'class=' in l]
    assert banner, 'provisional header must be a styled banner element'


def test_escaping_is_total():
    nasty = '# t\n\nnote: <img src=x onerror=alert(1)> & "quoted" \'sq\'\n'
    html = render_html(nasty)
    assert '<img' not in html
    assert '&lt;img src=x onerror=alert(1)&gt;' in html
    assert '&amp;' in html
    assert '&quot;quoted&quot;' in html
    assert '&#x27;sq&#x27;' in html
    # entities must not double-decode: raw & from input is &amp; exactly
    assert html.count('&amp;') >= 1 and '&amp;lt;' not in html


def test_fenced_block_content_is_escaped_text():
    md = '# t\n\n## s\n\n```\na < b & c > d\n```\n'
    html = render_html(md)
    assert '<pre><code>\na &lt; b &amp; c &gt; d\n</code></pre>' in html


def test_unknown_markdown_is_literal_text():
    md = '# t\n\n**bold** and [l](https://x)\n\n### deep\n'
    html = render_html(md)
    assert '**bold**' in html
    assert 'https://x' in html  # literal text, not a link
    assert '<a ' not in html and '<strong>' not in html
    assert '<h3>' not in html and '### deep' in html


def test_unicode_passes_through():
    md = '# t\n\ndose 5 µg, café — naïve\n'
    html = render_html(md)
    assert '5 µg, café — naïve' in html


def test_deterministic():
    assert render_html(REPORT) == render_html(REPORT)


def test_demo_html_wrapper():
    assert run_demo_html(CASES) == render_html(run_demo(CASES))
    assert run_demo_html(CASES) == render_html(REPORT)
    with pytest.raises(ValueError):
        run_demo_html(CASES, seed=True)
