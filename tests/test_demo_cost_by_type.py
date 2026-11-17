"""Tests for spec 031: demo per-error-type cost block for the LLM lane."""
import io
import json
from contextlib import redirect_stdout
from pathlib import Path

import pytest

from medcode_audit.demo import (main, run_demo, run_demo_cost,
                                run_demo_cost_by_type)
from medcode_audit.schema import ERROR_TYPES

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / 'data' / 'synthetic'
SNAPSHOT = json.loads(
    (ROOT / 'data' / 'regression' / 'llm-cost-by-type-snapshot.json').read_text())


def test_run_demo_cost_by_type_matches_committed_snapshot():
    out = run_demo_cost_by_type(CASES)
    snap = SNAPSHOT['seeds']['0']
    assert 'llm lane (gold-truth canned transport), seed 0, by error type' in out
    assert out.count('COST/LATENCY (PROVISIONAL)') == len(ERROR_TYPES)
    for etype in ERROR_TYPES:
        block = snap[etype]
        assert f'{etype}\n' in out
        assert f"calls {block['calls']}" in out
        if block['calls']:
            assert f"prompt {block['prompt_chars']} in" in out
            assert f"reply {block['reply_chars']} out" in out
        else:
            assert 'no calls recorded' in out


def test_run_demo_cost_by_type_orders_types_like_schema():
    out = run_demo_cost_by_type(CASES)
    positions = [out.index(f'{etype}\n') for etype in ERROR_TYPES]
    assert positions == sorted(positions)


def test_run_demo_cost_by_type_validation_and_determinism():
    with pytest.raises(ValueError):
        run_demo_cost_by_type(CASES, seed=True)
    with pytest.raises(ValueError):
        run_demo_cost_by_type(CASES, seed='0')
    with pytest.raises(ValueError):
        run_demo_cost_by_type(ROOT / 'data' / 'no-such-dir')
    assert run_demo_cost_by_type(CASES) == run_demo_cost_by_type(CASES)


def test_main_cost_by_type_flag_appends_blocks_and_rejects_unknown():
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = main(['--cost-by-type'])
    assert rc == 0
    out = buf.getvalue()
    assert out.startswith(run_demo() + '\n')
    assert 'by error type' in out
    assert out.count('COST/LATENCY (PROVISIONAL)') == len(ERROR_TYPES)
    with pytest.raises(ValueError):
        main(['--cost-by-type', '--nope'])


def test_main_combines_cost_flags_default_and_cost_stay_byte_identical():
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = main(['--cost', '--cost-by-type'])
    assert rc == 0
    out = buf.getvalue()
    assert out.startswith(run_demo() + '\n' + run_demo_cost() + '\n')
    assert 'by error type' in out
    buf = io.StringIO()
    with redirect_stdout(buf):
        main(['--cost'])
    assert buf.getvalue() == run_demo() + '\n' + run_demo_cost() + '\n'
    buf = io.StringIO()
    with redirect_stdout(buf):
        main()
    assert buf.getvalue() == run_demo() + '\n'
