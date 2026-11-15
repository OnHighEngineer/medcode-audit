"""Tests for spec 029: demo cost block for the LLM lane."""
import io
import json
from contextlib import redirect_stdout
from pathlib import Path

import pytest

from medcode_audit.cost_latency import (format_cost_latency,
                                        format_cost_summary,
                                        make_tracking_transport,
                                        summarize_records)
from medcode_audit.demo import main, run_demo, run_demo_cost

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / 'data' / 'synthetic'
SNAPSHOT = json.loads(
    (ROOT / 'data' / 'regression' / 'llm-cost-snapshot.json').read_text())
GOOD = {'calls': 2, 'total_latency': 2, 'mean_latency': 1.0,
        'prompt_chars': 10, 'reply_chars': 6}


def test_format_cost_summary_validation():
    with pytest.raises(ValueError):
        format_cost_summary('nope')
    with pytest.raises(ValueError):
        format_cost_summary({**GOOD, 'extra': 1})
    with pytest.raises(ValueError):
        format_cost_summary({k: v for k, v in GOOD.items() if k != 'calls'})
    with pytest.raises(ValueError):
        format_cost_summary({**GOOD, 'calls': True})
    with pytest.raises(ValueError):
        format_cost_summary({**GOOD, 'prompt_chars': -1})
    with pytest.raises(ValueError):
        format_cost_summary({**GOOD, 'mean_latency': 'fast'})
    with pytest.raises(ValueError):
        format_cost_summary({**GOOD, 'calls': 0, 'mean_latency': 1.0})


def test_format_cost_latency_delegates_to_summary():
    tracked, records = make_tracking_transport(lambda p: 'reply', iter(range(100)).__next__)
    tracked('prompt one')
    tracked('prompt two')
    assert format_cost_latency(records) == format_cost_summary(summarize_records(records))


def test_run_demo_cost_matches_committed_snapshot():
    out = run_demo_cost(CASES)
    snap = SNAPSHOT['seeds']['0']
    assert 'COST/LATENCY (PROVISIONAL)' in out
    assert 'llm lane (gold-truth canned transport), seed 0' in out
    assert f"calls {snap['calls']}" in out
    assert f"prompt {snap['prompt_chars']} in" in out
    assert f"reply {snap['reply_chars']} out" in out


def test_run_demo_cost_validation_and_determinism():
    with pytest.raises(ValueError):
        run_demo_cost(CASES, seed=True)
    with pytest.raises(ValueError):
        run_demo_cost(CASES, seed='0')
    with pytest.raises(ValueError):
        run_demo_cost(ROOT / 'data' / 'no-such-dir')
    assert run_demo_cost(CASES) == run_demo_cost(CASES)


def test_main_cost_flag_appends_block_and_rejects_unknown_args():
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = main(['--cost'])
    assert rc == 0
    out = buf.getvalue()
    assert out.startswith(run_demo() + '\n')
    assert 'COST/LATENCY (PROVISIONAL)' in out
    with pytest.raises(ValueError):
        main(['--nope'])
