"""Tests for spec 039: demo --seed flag."""
import io
from contextlib import redirect_stdout

import pytest

from medcode_audit.demo import (main, run_demo, run_demo_cost,
                                run_demo_cost_by_type, run_demo_html)


def _run(argv):
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = main(argv)
    return rc, buf.getvalue()


def test_seed_zero_matches_default_output():
    rc, out = _run(['--seed', '0'])
    assert rc == 0
    assert out == run_demo() + '\n'


def test_seed_selects_the_eval_seed():
    rc, out = _run(['--seed', '1'])
    assert rc == 0
    assert out == run_demo(seed=1) + '\n'
    assert out != run_demo() + '\n'


def test_seed_equals_form():
    rc, out = _run(['--seed=2'])
    assert rc == 0
    assert out == run_demo(seed=2) + '\n'


def test_seed_applies_to_cost_blocks():
    rc, out = _run(['--seed', '1', '--cost', '--cost-by-type'])
    assert rc == 0
    assert out == (run_demo(seed=1) + '\n' + run_demo_cost(seed=1) + '\n'
                   + run_demo_cost_by_type(seed=1) + '\n')


def test_seed_applies_to_html():
    rc, out = _run(['--seed=1', '--html'])
    assert rc == 0
    assert out == run_demo_html(seed=1) + '\n'


def test_seed_repeated_last_wins():
    rc, out = _run(['--seed', '0', '--seed', '1'])
    assert rc == 0
    assert out == run_demo(seed=1) + '\n'


def test_seed_without_value_raises():
    with pytest.raises(ValueError):
        main(['--seed'])


def test_seed_empty_equals_value_raises():
    with pytest.raises(ValueError):
        main(['--seed='])


def test_seed_non_integer_raises():
    for bad in ('abc', '1.5', '1_0', '+1', '--cost'):
        with pytest.raises(ValueError):
            main(['--seed', bad])
