"""Tests for spec 036: comma-separated lane names in self-check --only."""
import io
from contextlib import redirect_stdout

import pytest

from medcode_audit.regression import main


def _run(argv):
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = main(argv)
    return rc, buf.getvalue().splitlines()


def test_only_comma_separated_names():
    rc, lines = _run(['--only', 'baseline,llm_cost'])
    assert rc == 0
    assert lines == ['baseline: OK', 'llm_cost: OK']


def test_only_comma_mixes_with_repeated_flags():
    rc, lines = _run(['--only', 'demo_html,baseline', '--only', 'llm_cost'])
    assert rc == 0
    assert lines == ['baseline: OK', 'llm_cost: OK', 'demo_html: OK']


def test_only_comma_trailing_comma_raises():
    with pytest.raises(ValueError):
        main(['--only', 'baseline,'])


def test_only_comma_empty_value_raises():
    with pytest.raises(ValueError):
        main(['--only', ','])


def test_only_comma_unknown_segment_raises():
    with pytest.raises(ValueError):
        main(['--only', 'baseline,not-a-lane'])


def test_only_comma_whitespace_is_not_trimmed():
    with pytest.raises(ValueError):
        main(['--only', 'baseline, llm_cost'])
