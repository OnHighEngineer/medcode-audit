import io
import json
from contextlib import redirect_stdout
from pathlib import Path

import pytest

from medcode_audit.demo import DEMO_SEED, main, run_demo
from medcode_audit.report import generate_report
from medcode_audit.baseline import audit_baseline
from medcode_audit.failure_analysis import analyze_run
from medcode_audit.regression import load_regression_cases
from medcode_audit.runner import run_eval

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / 'data' / 'synthetic'


def test_seed_constant():
    assert DEMO_SEED == 0


def test_run_demo_matches_assembled_pipeline():
    demo = run_demo(CASES)
    cases = load_regression_cases(CASES)
    run = run_eval(cases, audit_baseline, seed=0)
    expected = generate_report(run, analyze_run(run, cases))
    assert demo == expected


def test_run_demo_default_dir_equals_explicit():
    assert run_demo() == run_demo(CASES)


def test_run_demo_carries_provisional_header():
    out = run_demo(CASES)
    assert out.startswith('# medcode-audit eval report')
    assert 'PROVISIONAL' in out
    assert '%' not in out


def test_run_demo_validation():
    with pytest.raises(ValueError):
        run_demo(CASES, seed=True)
    with pytest.raises(ValueError):
        run_demo(CASES, seed='0')
    with pytest.raises(ValueError):
        run_demo(ROOT / 'data' / 'no-such-dir')


def test_main_prints_exactly_run_demo():
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = main()
    assert rc == 0
    assert buf.getvalue() == run_demo() + '\n'


def test_demo_output_is_valid_report_input_for_regression_snapshot():
    # The demo must read the same 50 cases the regression suite guards.
    out = run_demo(CASES)
    snap = json.loads((ROOT / 'data' / 'regression' / 'baseline-snapshot.json').read_text())
    seed0 = snap['seeds']['0']
    for etype, row in seed0.items():
        if row['applicable']:
            assert f"{etype}: detected {row['detected']}/{row['applicable']}" in out
        else:
            total = row['inapplicable']
            assert f"{etype}: not implemented" in out and f"{total} cases skipped" in out
