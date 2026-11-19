"""Tests for spec 033: demo --html output flag."""
import io
from contextlib import redirect_stdout
from pathlib import Path

import pytest

from medcode_audit.demo import (main, run_demo, run_demo_cost,
                                run_demo_cost_by_type, run_demo_html)

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / 'data' / 'synthetic'


def _capture(args):
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = main(args)
    return rc, buf.getvalue()


def test_main_html_prints_exactly_run_demo_html():
    rc, out = _capture(['--html'])
    assert rc == 0
    assert out == run_demo_html() + '\n'
    assert out.startswith('<!DOCTYPE html>')


def test_main_html_is_exclusive_with_cost_flags():
    with pytest.raises(ValueError):
        main(['--html', '--cost'])
    with pytest.raises(ValueError):
        main(['--html', '--cost-by-type'])
    with pytest.raises(ValueError):
        main(['--html', '--cost', '--cost-by-type'])


def test_main_other_outputs_stay_byte_identical():
    rc, out = _capture([])
    assert rc == 0
    assert out == run_demo() + '\n'
    rc, out = _capture(['--cost'])
    assert rc == 0
    assert out == run_demo() + '\n' + run_demo_cost() + '\n'
    rc, out = _capture(['--cost-by-type'])
    assert rc == 0
    assert out == run_demo() + '\n' + run_demo_cost_by_type() + '\n'
    with pytest.raises(ValueError):
        main(['--html', '--nope'])
