"""Offline demo entry point. See docs/specs/023-demo-script.md.

One command runs the whole pipeline on the committed synthetic cases -
spec-005 eval with the spec-008 rule baseline, spec-017 failure analysis,
spec-019 report - and prints the report a reviewer would read. No
transports, no network, deterministic. Counts stay provisional.
"""
from __future__ import annotations

from pathlib import Path

from .baseline import audit_baseline
from .failure_analysis import analyze_run
from .html_report import render_html
from .regression import load_regression_cases
from .report import generate_report
from .runner import run_eval

DEMO_SEED = 0

_DEFAULT_CASE_DIR = Path(__file__).resolve().parents[2] / 'data' / 'synthetic'


def run_demo(case_dir=None, seed=DEMO_SEED) -> str:
    """Return the assembled eval report for the cases in case_dir."""
    if type(seed) is not int:
        raise ValueError('seed must be an int')
    directory = _DEFAULT_CASE_DIR if case_dir is None else Path(case_dir)
    cases = load_regression_cases(directory)
    run = run_eval(cases, audit_baseline, seed=seed)
    return generate_report(run, analyze_run(run, cases))


def run_demo_html(case_dir=None, seed=DEMO_SEED) -> str:
    """Return run_demo rendered as a standalone HTML page (spec 025)."""
    return render_html(run_demo(case_dir, seed))


def main() -> int:
    print(run_demo())
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
