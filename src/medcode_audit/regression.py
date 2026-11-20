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
from .canned_llm import make_gold_transport, make_noisy_transport
from .cost_latency import make_tracking_transport, summarize_records
from .llm_auditor import make_llm_auditor
from .runner import run_eval
from .schema import ERROR_TYPES

REGRESSION_SEEDS = (0, 1, 2)

LANES = ('baseline', 'llm', 'noisy_wrong_verdict', 'noisy_fabricated_quote',
         'noisy_dropped_verdict')

_NOISY_CORRUPTION = {f'noisy_{c}': c
                     for c in ('wrong_verdict', 'fabricated_quote', 'dropped_verdict')}

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
    if lane == 'baseline':
        auditor = audit_baseline
    elif lane == 'llm':
        auditor = make_llm_auditor(make_gold_transport(cases))
    else:
        auditor = make_llm_auditor(
            make_noisy_transport(cases, _NOISY_CORRUPTION[lane]))
    out = {'case_count': len(cases), 'seeds': {}}
    for seed in seeds:
        try:
            run = run_eval(cases, auditor, seed=seed)
        except ValueError as exc:
            if lane not in _NOISY_CORRUPTION:
                raise
            out['seeds'][str(seed)] = {'validation_error': str(exc)}
            continue
        out['seeds'][str(seed)] = {
            etype: {field: run['tally'][etype][field] for field in _ROW_FIELDS}
            for etype in run['tally']
        }
    return out


def run_llm_cost(cases, seeds=REGRESSION_SEEDS) -> dict:
    """Snapshot spec-018 cost accounting for the llm lane, beside the tally."""
    if not isinstance(cases, list) or any(not isinstance(c, dict) for c in cases):
        raise ValueError('cases must be a list of dicts')
    if not _valid_seeds(seeds):
        raise ValueError('seeds must be a tuple or list of ints')
    out = {'case_count': len(cases), 'seeds': {}}
    for seed in seeds:
        ticks = iter(range(1_000_000_000))  # deterministic clock: +1 per reading
        clock = lambda: next(ticks)
        tracked, records = make_tracking_transport(make_gold_transport(cases), clock)
        run_eval(cases, make_llm_auditor(tracked), seed=seed)
        out['seeds'][str(seed)] = summarize_records(records)
    return out


def run_llm_cost_by_type(cases, seeds=REGRESSION_SEEDS) -> dict:
    """Snapshot spec-018 cost accounting per error type for the llm lane.

    Runs the eval once per error type with its own tracked transport, so
    each summary attributes calls/characters to exactly one type. The
    per-type sums equal the combined run_llm_cost totals. See
    docs/specs/030-llm-cost-by-type.md.
    """
    if not isinstance(cases, list) or any(not isinstance(c, dict) for c in cases):
        raise ValueError('cases must be a list of dicts')
    if not _valid_seeds(seeds):
        raise ValueError('seeds must be a tuple or list of ints')
    out = {'case_count': len(cases), 'seeds': {}}
    for seed in seeds:
        per_type = {}
        for etype in ERROR_TYPES:
            ticks = iter(range(1_000_000_000))  # same deterministic clock as run_llm_cost
            clock = lambda: next(ticks)
            tracked, records = make_tracking_transport(
                make_gold_transport(cases), clock)
            run_eval(cases, make_llm_auditor(tracked),
                     error_types=(etype,), seed=seed)
            per_type[etype] = summarize_records(records)
        out['seeds'][str(seed)] = per_type
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


SELF_CHECK_LANES = ('baseline', 'llm', 'noisy_wrong_verdict',
                    'noisy_fabricated_quote', 'noisy_dropped_verdict',
                    'llm_cost', 'llm_cost_by_type',
                    'demo_report', 'demo_html')

_DEFAULT_DATA_DIR = Path(__file__).resolve().parents[2] / 'data'

_ARTIFACTS = {'demo_report': 'day-27-demo-output.md',
              'demo_html': 'day-29-demo-report.html'}


def _text_drift(artifact, live) -> list:
    """Return [] when the committed artifact matches live output byte-exact."""
    if not artifact.is_file():
        raise ValueError(f'not a file: {artifact}')
    expected = artifact.read_text()
    if expected == live:
        return []
    problems = []
    exp_lines = expected.splitlines()
    live_lines = live.splitlines()
    for i, (a, b) in enumerate(zip(exp_lines, live_lines), 1):
        if a != b:
            problems.append(
                f'{artifact.name} line {i}: expected {a!r}, live {b!r}')
            break
    if len(exp_lines) != len(live_lines):
        problems.append(f'{artifact.name} line count: '
                        f'expected {len(exp_lines)}, live {len(live_lines)}')
    return problems


def check_committed_snapshots(data_dir=None, reviews_dir=None) -> dict:
    """Re-run every lane and diff each against its committed snapshot (spec 032).

    Returns {lane: [problems]} in SELF_CHECK_LANES order; an empty list
    means the lane matches its committed snapshot.
    """
    root = _DEFAULT_DATA_DIR if data_dir is None else Path(data_dir)
    if not root.is_dir():
        raise ValueError(f'not a directory: {root}')
    cases = load_regression_cases(root / 'synthetic')
    reg = root / 'regression'
    expected = {
        'baseline': json.loads((reg / 'baseline-snapshot.json').read_text()),
        'llm': json.loads((reg / 'llm-snapshot.json').read_text()),
        'llm_cost': json.loads((reg / 'llm-cost-snapshot.json').read_text()),
        'llm_cost_by_type': json.loads(
            (reg / 'llm-cost-by-type-snapshot.json').read_text()),
    }
    noisy = json.loads((reg / 'noisy-snapshot.json').read_text())
    out = {}
    out['baseline'] = check_snapshot(run_regression(cases), expected['baseline'])
    out['llm'] = check_snapshot(run_regression(cases, lane='llm'),
                                expected['llm'])
    for lane in LANES[2:]:
        out[lane] = check_snapshot(run_regression(cases, lane=lane),
                                   noisy['lanes'][lane])
    out['llm_cost'] = check_snapshot(run_llm_cost(cases), expected['llm_cost'])
    out['llm_cost_by_type'] = check_snapshot(run_llm_cost_by_type(cases),
                                             expected['llm_cost_by_type'])
    from .demo import run_demo, run_demo_html  # lazy: demo imports regression
    reviews = (Path(__file__).resolve().parents[2] / 'docs' / 'reviews'
               if reviews_dir is None else Path(reviews_dir))
    out['demo_report'] = _text_drift(reviews / _ARTIFACTS['demo_report'],
                                     run_demo())
    out['demo_html'] = _text_drift(reviews / _ARTIFACTS['demo_html'],
                                   run_demo_html())
    return out


def main(argv=None) -> int:
    """Print one OK/drift line per lane; exit 0 when all match (spec 032)."""
    args = list(argv) if argv is not None else []
    if args:
        raise ValueError(f'unknown arguments: {args}')
    results = check_committed_snapshots()
    drift = 0
    for lane in SELF_CHECK_LANES:
        problems = results[lane]
        if problems:
            drift += 1
            print(f'{lane}: DRIFT ({len(problems)} problems)')
            for problem in problems:
                print(f'  {problem}')
        else:
            print(f'{lane}: OK')
    return 1 if drift else 0


if __name__ == '__main__':
    import sys
    raise SystemExit(main(sys.argv[1:]))
