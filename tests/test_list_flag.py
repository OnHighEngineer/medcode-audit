"""Tests for spec 037: self-check --list flag."""
import io
from contextlib import redirect_stdout

import pytest

from medcode_audit.regression import SELF_CHECK_LANES, main


def test_list_prints_lane_names_and_exits_zero():
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = main(['--list'])
    assert rc == 0
    assert buf.getvalue().splitlines() == list(SELF_CHECK_LANES)


def test_list_with_only_raises():
    with pytest.raises(ValueError):
        main(['--list', '--only', 'baseline'])


def test_list_twice_raises():
    with pytest.raises(ValueError):
        main(['--list', '--list'])


def test_list_with_unknown_arg_raises():
    with pytest.raises(ValueError):
        main(['--list', '--fix'])
