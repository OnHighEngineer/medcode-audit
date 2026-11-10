"""Regression snapshot for the rule-baseline eval. See docs/specs/022-regression-suite.md.

Re-runs the full synthetic case set through the spec-005 runner with the
spec-008 rule baseline at fixed seeds and diffs every tally number and
inapplicability reason against a committed snapshot. Drift in the injector,
runner, baseline, assertion, missed-code or upcoding layers becomes a failing
test that names the drifted number. Records actual behavior; it does not
re-validate labels (milestone 6). Counts stay provisional.
"""
from __future__ import annotations

import json
from pathlib import Path

from .baseline import audit_baseline
from .canned_llm import make_gold_transport
from .llm_auditor import make_llm_auditor
from .runner import run_eval

REGRESSION_SEEDS = (0, 1, 2)

LANES = ('baseline', 'llm')

_ROW_FIELDS = ('applicable', 'detected', 'not_detected', 'inapplicable',
               'false_flags', 'reasons')


def _valid_seeds(seeds):
    return (isinstance(seeds, (tuple, list))
            and all(type(s) is int for s in seeds))


def _valid_snapshot(d):
    return (isinstance(d, dict)
            and isinstance(d.get('case_count'), int)
            and not isinstance(d.get('case_count'), bool)
            and isinstance(d.get('seeds'), dict))


def load_regression_cases(directory) -> list:
    """Return the raw case dicts from every *.json in directory, sorted by name."""
    root = Path(directory)
    if not root.is_dir():
        raise ValueError(f'not a directory: {directory}')
    cases = []
    for path in sorted(root.glob('*.json')):
        data = json.loads(path.read_text())
        if not isinstance(data, dict):
            raise ValueError(f'case file is not an object: {path.name}')
        cases.append(data)
    return cases


def run_regression(cases, seeds=REGRESSION_SEEDS, lane='baseline') -> dict:
    """Snapshot the eval tally over cases for each seed and lane."""
    if not isinstance(cases, list) or any(not isinstance(c, dict) for c in cases):
        raise ValueError('cases must be a list of dicts')
    if not _valid_seeds(seeds):
        raise ValueError('seeds must be a tuple or list of ints')
    if lane not in LANES:
        raise ValueError(f'lane must be one of {LANES}')
    auditor = (audit_baseline if lane == 'baseline'
               else make_llm_auditor(make_gold_transport(cases)))
    out = {'case_count': len(cases), 'seeds': {}}
    for seed in seeds:
        run = run_eval(cases, auditor, seed=seed)
        out['seeds'][str(seed)] = {
            etype: {field: run['tally'][etype][field] for field in _ROW_FIELDS}
            for etype in run['tally']
        }
    return out


def _diff(path, live, expected, problems):
    if isinstance(expected, dict) and isinstance(live, dict):
        for key in expected:
            if key not in live:
                problems.append(f'{path}{key}: expected present, absent in live')
            else:
                _diff(f'{path}{key}.', live[key], expected[key], problems)
        for key in live:
            if key not in expected:
                problems.append(f'{path}{key}: absent in expected, present in live')
    elif live != expected:
        problems.append(f'{path[:-1]}: expected {expected!r}, got {live!r}')


def check_snapshot(live, expected) -> list:
    """Return [] when live matches expected, else one string per mismatch."""
    if not _valid_snapshot(live):
        raise ValueError('live must be a run_regression snapshot dict')
    if not _valid_snapshot(expected):
        raise ValueError('expected must be a run_regression snapshot dict')
    problems = []
    _diff('', live, expected, problems)
    return problems
