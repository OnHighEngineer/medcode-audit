import json
from pathlib import Path

import pytest

from medcode_audit.canned_llm import make_gold_transport, make_noisy_transport
from medcode_audit.llm_auditor import build_prompt, make_llm_auditor
from medcode_audit.regression import (check_snapshot, load_regression_cases,
                                      run_regression)

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / 'data' / 'regression' / 'noisy-snapshot.json'
NOISY = ('noisy_wrong_verdict', 'noisy_fabricated_quote', 'noisy_dropped_verdict')


def cases():
    return load_regression_cases(ROOT / 'data' / 'synthetic')


def _case_with_gold(batch):
    return next(c for c in batch if c['gold_codes'])


def test_noisy_transport_validation():
    batch = cases()
    with pytest.raises(ValueError):
        make_noisy_transport('nope', 'wrong_verdict')
    with pytest.raises(ValueError):
        make_noisy_transport(batch, 'loud_verdict')
    with pytest.raises(ValueError):
        make_noisy_transport(batch, 0)


def test_wrong_verdict_flips_first_gold_claim():
    batch = cases()
    case = _case_with_gold(batch)
    claimed = [g['code'] for g in case['gold_codes']]
    reply = json.loads(make_noisy_transport(batch, 'wrong_verdict')(
        build_prompt(case['note_text'], claimed)))
    by_code = {v['code']: v['verdict'] for v in reply['verdicts']}
    assert by_code[claimed[0]] == 'UNSUPPORTED'
    assert all(by_code[c] == 'SUPPORTED' for c in claimed[1:])


def test_fabricated_quote_marker_and_clean_fallback():
    batch = cases()
    case = _case_with_gold(batch)
    reply = json.loads(make_noisy_transport(batch, 'fabricated_quote')(
        build_prompt(case['note_text'], [case['gold_codes'][0]['code']])))
    assert reply['verdicts'][0]['evidence_quote'] == 'FABRICATED QUOTE NOT IN NOTE'
    empty = next(c for c in batch if not c['gold_codes'])
    clean = json.loads(make_noisy_transport(batch, 'fabricated_quote')(
        build_prompt(empty['note_text'], ['Z99.99'])))
    assert all('evidence_quote' not in v for v in clean['verdicts'])


def test_dropped_verdict_omits_first():
    batch = cases()
    case = _case_with_gold(batch)
    claimed = [g['code'] for g in case['gold_codes']]
    reply = json.loads(make_noisy_transport(batch, 'dropped_verdict')(
        build_prompt(case['note_text'], claimed)))
    assert [v['code'] for v in reply['verdicts']] == claimed[1:]


def test_lane_names_accepted_and_unknown_rejected():
    batch = cases()
    for lane in NOISY:
        run_regression(batch[:1], seeds=(0,), lane=lane)
    with pytest.raises(ValueError):
        run_regression(batch, lane='noisy_typo')


def test_wrong_verdict_lane_detects_but_false_flags():
    snap = run_regression(cases(), lane='noisy_wrong_verdict')
    total_false = 0
    for seed_snap in snap['seeds'].values():
        for row in seed_snap.values():
            assert row['detected'] == row['applicable']
            assert row['not_detected'] == 0
            total_false += row['false_flags']
    assert total_false > 0


def test_rejecting_lanes_fail_closed_with_named_error():
    for lane, needle in (('noisy_fabricated_quote', 'verbatim note substring'),
                         ('noisy_dropped_verdict', 'cover exactly')):
        snap = run_regression(cases(), lane=lane)
        for seed_snap in snap['seeds'].values():
            assert set(seed_snap) == {'validation_error'}
            assert needle in seed_snap['validation_error']


def test_noisy_lanes_deterministic():
    batch = cases()
    for lane in NOISY:
        assert run_regression(batch, lane=lane) == run_regression(batch, lane=lane)


def test_existing_lanes_untouched():
    batch = cases()
    assert run_regression(batch) == run_regression(batch, lane='baseline')
    llm = json.loads((ROOT / 'data' / 'regression' / 'llm-snapshot.json').read_text())
    assert check_snapshot(run_regression(batch, lane='llm'), llm) == []


def test_committed_noisy_snapshot_matches_live():
    committed = json.loads(SNAPSHOT.read_text())
    assert set(committed['lanes']) == set(NOISY)
    batch = cases()
    for lane in NOISY:
        live = run_regression(batch, lane=lane)
        assert check_snapshot(live, committed['lanes'][lane]) == []
