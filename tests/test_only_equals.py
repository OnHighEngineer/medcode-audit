"""Tests for spec 038: equals form for self-check --only."""
import io
from contextlib import redirect_stdout

import pytest

from medcode_audit.regression import main


def _run(argv):
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = main(argv)
    return rc, buf.getvalue().splitlines()


def test_only_equals_runs_one_lane():
    rc, lines = _run(['--only=llm_cost'])
    assert rc == 0
    assert lines == ['llm_cost: OK']


def test_only_equals_takes_comma_names():
    rc, lines = _run(['--only=llm_cost,baseline'])
    assert rc == 0
    assert lines == ['baseline: OK', 'llm_cost: OK']


def test_only_equals_mixes_with_space_form():
    rc, lines = _run(['--only=demo_html', '--only', 'llm_cost'])
    assert rc == 0
    assert lines == ['llm_cost: OK', 'demo_html: OK']


def test_only_equals_empty_value_raises():
    with pytest.raises(ValueError):
        main(['--only='])


def test_only_equals_unknown_lane_raises():
    with pytest.raises(ValueError):
        main(['--only=not-a-lane'])


def test_only_equals_untrimmed_name_raises():
    with pytest.raises(ValueError):
        main(['--only= baseline'])


def test_list_with_only_equals_raises():
    with pytest.raises(ValueError):
        main(['--list', '--only=baseline'])
