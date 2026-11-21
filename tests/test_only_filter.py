"""Tests for spec 035: self-check --only filter."""
import io
from contextlib import redirect_stdout

import pytest

from medcode_audit.regression import (SELF_CHECK_LANES,
                                      check_committed_snapshots, main)


def _run(argv):
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = main(argv)
    return rc, buf.getvalue().splitlines()


def test_only_runs_one_lane():
    rc, lines = _run(['--only', 'llm_cost'])
    assert rc == 0
    assert lines == ['llm_cost: OK']


def test_only_keeps_lane_order_not_argument_order():
    rc, lines = _run(['--only', 'demo_html', '--only', 'baseline'])
    assert rc == 0
    assert lines == ['baseline: OK', 'demo_html: OK']


def test_only_duplicate_names_collapse():
    rc, lines = _run(['--only', 'baseline', '--only', 'baseline'])
    assert rc == 0
    assert lines == ['baseline: OK']


def test_only_unknown_lane_raises():
    with pytest.raises(ValueError):
        main(['--only', 'not-a-lane'])


def test_only_without_value_raises():
    with pytest.raises(ValueError):
        main(['--only'])


def test_only_mixed_with_unknown_arg_raises():
    with pytest.raises(ValueError):
        main(['--only', 'baseline', '--fix'])


def test_check_committed_snapshots_only_returns_requested_lanes():
    results = check_committed_snapshots(only=('llm_cost',))
    assert tuple(results) == ('llm_cost',)
    assert results['llm_cost'] == []


def test_check_committed_snapshots_only_keeps_lane_order():
    results = check_committed_snapshots(only=('demo_html', 'baseline'))
    assert tuple(results) == ('baseline', 'demo_html')
    for lane in results:
        assert results[lane] == []


def test_check_committed_snapshots_only_unknown_lane_raises():
    with pytest.raises(ValueError):
        check_committed_snapshots(only=('not-a-lane',))


def test_check_committed_snapshots_only_none_is_full_contract():
    results = check_committed_snapshots(only=None)
    assert tuple(results) == SELF_CHECK_LANES
