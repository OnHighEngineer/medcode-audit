"""Tests for spec 027: narrow-viewport HTML report polish."""
from pathlib import Path

from medcode_audit.demo import run_demo
from medcode_audit.html_report import render_html

ROOT = Path(__file__).resolve().parents[1]
REPORT = run_demo(ROOT / 'data' / 'synthetic')


def test_viewport_meta_present():
    html = render_html(REPORT)
    assert '<meta name="viewport" content="width=device-width, initial-scale=1">' in html


def test_narrow_media_query_wraps_fenced_blocks():
    html = render_html(REPORT)
    assert '@media (max-width:40em)' in html
    query = html.split('@media (max-width:40em)')[1]
    assert 'white-space:pre-wrap' in query
    assert 'overflow-wrap:anywhere' in query


def test_desktop_rule_unchanged():
    html = render_html(REPORT)
    style = html.split('<style>')[1].split('</style>')[0]
    default = style.split('@media')[0]
    assert 'overflow-x:auto' in default
    assert 'pre-wrap' not in default


def test_safety_guarantees_hold_with_media_query():
    html = render_html(REPORT)
    assert '<script' not in html.lower()
    assert 'http://' not in html and 'https://' not in html
    assert 'PROVISIONAL' in html


def test_content_and_escaping_unaffected():
    md = '# t\n\n```\na < b & ' + 'x' * 300 + '\n```\n'
    html = render_html(md)
    assert 'a &lt; b &amp; ' + 'x' * 300 in html
    assert render_html(md) == render_html(md)
