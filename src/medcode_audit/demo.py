"""Offline demo entry point. See docs/specs/023-demo-script.md.

One command runs the whole pipeline on the committed synthetic cases -
spec-005 eval with the spec-008 rule baseline, spec-017 failure analysis,
spec-019 report - and prints the report a reviewer would read. No
transports, no network, deterministic. Counts stay provisional.
"""
from __future__ import annotations

from pathlib import Path

from .baseline import audit_baseline
from .cost_latency import format_cost_summary
from .failure_analysis import analyze_run
from .html_report import render_html
from .regression import (load_regression_cases, run_llm_cost,
                         run_llm_cost_by_type)
from .report import generate_report
from .runner import run_eval
from .schema import ERROR_TYPES

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


def run_demo_cost(case_dir=None, seed=DEMO_SEED) -> str:
    """Return the llm lane's spec-018 cost/latency block for one seed (spec 029)."""
    if type(seed) is not int:
        raise ValueError('seed must be an int')
    directory = _DEFAULT_CASE_DIR if case_dir is None else Path(case_dir)
    cases = load_regression_cases(directory)
    summary = run_llm_cost(cases, seeds=(seed,))['seeds'][str(seed)]
    return (f'llm lane (gold-truth canned transport), seed {seed}\n'
            + format_cost_summary(summary))


def run_demo_cost_by_type(case_dir=None, seed=DEMO_SEED) -> str:
    """Return one spec-018 cost block per error type for one seed (spec 031)."""
    if type(seed) is not int:
        raise ValueError('seed must be an int')
    directory = _DEFAULT_CASE_DIR if case_dir is None else Path(case_dir)
    cases = load_regression_cases(directory)
    per_type = run_llm_cost_by_type(cases, seeds=(seed,))['seeds'][str(seed)]
    blocks = [f'llm lane (gold-truth canned transport), seed {seed}, by error type\n']
    for etype in ERROR_TYPES:
        blocks.append(f'{etype}\n' + format_cost_summary(per_type[etype]))
    return '\n'.join(blocks)


def main(argv=None) -> int:
    args = list(argv) if argv is not None else []
    unknown = [a for a in args if a not in ('--cost', '--cost-by-type')]
    if unknown:
        raise ValueError(f'unknown arguments: {unknown}')
    print(run_demo())
    if '--cost' in args:
        print(run_demo_cost())
    if '--cost-by-type' in args:
        print(run_demo_cost_by_type())
    return 0


if __name__ == '__main__':
    import sys
    raise SystemExit(main(sys.argv[1:]))
