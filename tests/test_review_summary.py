"""Tests for spec 040: label review summary command."""
import io
from contextlib import redirect_stdout

import pytest

from medcode_audit.review import (build_review_sheet, dump_sheet,
                                  format_review_summary, main,
                                  summarize_review)

CASES = [
    {'id': 'c1', 'note_text': 'Confirmed diagnosis: x',
     'gold_codes': [{'code': 'E11.9',
                     'evidence_quote': 'Confirmed diagnosis: x'}]},
    {'id': 'c2', 'note_text': 'no markers here', 'gold_codes': []},
]


def _sheet(marks):
    sheet = build_review_sheet(CASES)
    for row, mark in zip(sheet['rows'], marks):
        row['reviewer_mark'] = mark
        if mark == 'disagree':
            row['reviewer_note'] = 'quote does not support'
    return sheet


def _run(argv):
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = main(argv)
    return rc, buf.getvalue()


def test_format_renders_counts_and_disagreements():
    summary = summarize_review(_sheet(['agree', 'disagree']))
    assert format_review_summary(summary) == (
        'LABEL REVIEW SUMMARY (PROVISIONAL): counts only; disagreements are\n'
        'fixed via a logged decision-log entry.\n'
        '\n'
        'total rows: 2\n'
        'reviewed: 2\n'
        'unreviewed: 0\n'
        'agree: 1\n'
        'disagree: 1\n'
        '\n'
        'disagreements:\n'
        '- c2 [control] quote does not support'
    )


def test_format_renders_no_disagreements():
    summary = summarize_review(_sheet(['agree', 'agree']))
    out = format_review_summary(summary)
    assert out.endswith('disagreements: none')
    assert '%' not in out


def test_format_renders_unreviewed_rows():
    summary = summarize_review(_sheet([None, 'agree']))
    out = format_review_summary(summary)
    assert 'reviewed: 1\n' in out
    assert 'unreviewed: 1\n' in out


def test_format_validation():
    summary = summarize_review(_sheet(['agree', 'agree']))
    for bad in ({}, {**summary, 'extra': 1},
                {**summary, 'agree': True},
                {**summary, 'reviewed': -1},
                {**summary, 'disagreements': [{'case_id': 'c1'}]},
                {**summary, 'disagreements': [
                    {'case_id': 'c1', 'gold_code': 1, 'reviewer_note': ''}]}):
        with pytest.raises(ValueError):
            format_review_summary(bad)


def test_main_summarizes_a_marked_sheet(tmp_path):
    path = tmp_path / 'marked.json'
    path.write_text(dump_sheet(_sheet(['disagree', 'agree'])))
    rc, out = _run([str(path)])
    assert rc == 0
    assert out == format_review_summary(
        summarize_review(_sheet(['disagree', 'agree']))) + '\n'


def test_main_argument_errors():
    for argv in ([], ['a.json', 'b.json'], ['--fix']):
        with pytest.raises(ValueError):
            main(argv)


def test_main_missing_or_invalid_sheet(tmp_path):
    with pytest.raises(ValueError):
        main([str(tmp_path / 'missing.json')])
    bad = tmp_path / 'bad.json'
    bad.write_text('not json')
    with pytest.raises(ValueError):
        main([str(bad)])


def test_main_is_deterministic(tmp_path):
    path = tmp_path / 'marked.json'
    path.write_text(dump_sheet(_sheet(['agree', 'disagree'])))
    assert _run([str(path)]) == _run([str(path)])
