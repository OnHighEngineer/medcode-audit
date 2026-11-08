import copy
import json

import pytest

from medcode_audit.regression import (REGRESSION_SEEDS, check_snapshot,
                                      load_regression_cases, run_regression)
from medcode_audit.schema import ERROR_TYPES

ROOT = __import__('pathlib').Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / 'data' / 'regression' / 'baseline-snapshot.json'


def cases():
    return load_regression_cases(ROOT / 'data' / 'synthetic')


def test_seed_constant():
    assert REGRESSION_SEEDS == (0, 1, 2)
    assert all(type(s) is int for s in REGRESSION_SEEDS)


def test_load_regression_cases_reads_all_sorted():
    loaded = cases()
    assert len(loaded) == 50
    assert all(isinstance(c, dict) for c in loaded)
    files = sorted((ROOT / 'data' / 'synthetic').glob('*.json'))
    expected_ids = [json.loads(p.read_text())['id'] for p in files]
    assert [c['id'] for c in loaded] == expected_ids


def test_load_regression_cases_rejects_missing_directory():
    with pytest.raises(ValueError):
        load_regression_cases(ROOT / 'data' / 'no-such-dir')


def test_run_regression_validation():
    batch = cases()
    with pytest.raises(ValueError):
        run_regression('not-a-list')
    with pytest.raises(ValueError):
        run_regression([{'id': 'x'}, 'not-a-dict'])
    with pytest.raises(ValueError):
        run_regression(batch, seeds='0')
    with pytest.raises(ValueError):
        run_regression(batch, seeds=[0, True])


def test_run_regression_shape_and_determinism():
    batch = cases()
    snap1 = run_regression(batch)
    snap2 = run_regression(batch)
    assert snap1 == snap2
    assert snap1['case_count'] == 50
    assert list(snap1['seeds']) == [str(s) for s in REGRESSION_SEEDS]
    for seed_snap in snap1['seeds'].values():
        assert list(seed_snap) == list(ERROR_TYPES)
        for etype, row in seed_snap.items():
            assert set(row) == {'applicable', 'detected', 'not_detected',
                                'inapplicable', 'false_flags', 'reasons'}
            assert (row['applicable'] == row['detected'] + row['not_detected'])
            assert isinstance(row['reasons'], dict)


def test_check_snapshot_validation():
    snap = run_regression(cases())
    with pytest.raises(ValueError):
        check_snapshot('nope', snap)
    with pytest.raises(ValueError):
        check_snapshot(snap, {'wrong': 'shape'})
    with pytest.raises(ValueError):
        check_snapshot({'case_count': 'x', 'seeds': {}}, snap)


def test_check_snapshot_names_mismatches():
    snap = run_regression(cases())
    assert check_snapshot(snap, copy.deepcopy(snap)) == []
    drifted = copy.deepcopy(snap)
    drifted['seeds']['0']['missed_code']['detected'] += 1
    drifted['seeds']['1']['unsupported_code']['reasons']['no_unmentioned_condition'] = 99
    problems = check_snapshot(snap, drifted)
    assert len(problems) == 2
    assert any('missed_code' in p and 'detected' in p for p in problems)
    assert any('unsupported_code' in p and 'reasons' in p for p in problems)


def test_committed_snapshot_matches_live_behavior():
    live = run_regression(cases())
    expected = json.loads(SNAPSHOT.read_text())
    assert check_snapshot(live, expected) == []
