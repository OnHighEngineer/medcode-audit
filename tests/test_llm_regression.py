import copy
import json
from pathlib import Path

import pytest

from medcode_audit.canned_llm import make_gold_transport
from medcode_audit.llm_auditor import build_prompt, make_llm_auditor
from medcode_audit.regression import (REGRESSION_SEEDS, check_snapshot,
                                      load_regression_cases, run_regression)
from medcode_audit.schema import ERROR_TYPES

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / 'data' / 'regression' / 'llm-snapshot.json'


def cases():
    return load_regression_cases(ROOT / 'data' / 'synthetic')


def test_gold_transport_validation():
    with pytest.raises(ValueError):
        make_gold_transport('not-a-list')
    with pytest.raises(ValueError):
        make_gold_transport([{'id': 'x'}, 'nope'])
    same_gold = [{'note_text': 'n', 'gold_codes': [{'code': 'A00', 'evidence_quote': 'q'}]},
                 {'note_text': 'n', 'gold_codes': [{'code': 'A00', 'evidence_quote': 'q'}]}]
    make_gold_transport(same_gold)  # identical gold on a repeated note is fine
    conflict = [{'note_text': 'n', 'gold_codes': [{'code': 'A00', 'evidence_quote': 'q'}]},
                {'note_text': 'n', 'gold_codes': [{'code': 'B01', 'evidence_quote': 'q'}]}]
    with pytest.raises(ValueError):
        make_gold_transport(conflict)


def test_gold_transport_replies_from_gold_truth():
    batch = cases()
    case = next(c for c in batch if c['gold_codes'])
    gold = {g['code']: g['evidence_quote'] for g in case['gold_codes']}
    claimed = list(gold) + ['Z99.99']
    transport = make_gold_transport(batch)
    reply = json.loads(transport(build_prompt(case['note_text'], claimed)))
    by_code = {v['code']: v for v in reply['verdicts']}
    for code, quote in gold.items():
        assert by_code[code]['verdict'] == 'SUPPORTED'
        assert by_code[code]['evidence_quote'] == quote
        assert quote in case['note_text']
    assert by_code['Z99.99']['verdict'] == 'UNSUPPORTED'
    assert reply['missed_codes'] == []


def test_gold_transport_missed_and_fail_closed():
    batch = cases()
    case = next(c for c in batch if len(c['gold_codes']) >= 2)
    gold = sorted(g['code'] for g in case['gold_codes'])
    transport = make_gold_transport(batch)
    reply = json.loads(transport(build_prompt(case['note_text'], [gold[0]])))
    assert reply['missed_codes'] == gold[1:]
    with pytest.raises(ValueError):
        transport(build_prompt('a note from no case', ['A00']))
    with pytest.raises(ValueError):
        transport('garbage prompt with no fences')


def test_lane_parameter_validation_and_default():
    batch = cases()
    with pytest.raises(ValueError):
        run_regression(batch, lane='gpt')
    with pytest.raises(ValueError):
        run_regression(batch, lane=0)
    assert run_regression(batch) == run_regression(batch, lane='baseline')


def test_llm_lane_shape_and_determinism():
    batch = cases()
    snap1 = run_regression(batch, lane='llm')
    snap2 = run_regression(batch, lane='llm')
    assert snap1 == snap2
    assert snap1['case_count'] == 50
    assert list(snap1['seeds']) == [str(s) for s in REGRESSION_SEEDS]
    for seed_snap in snap1['seeds'].values():
        assert list(seed_snap) == list(ERROR_TYPES)


def test_llm_lane_detects_everything_with_gold_truth():
    snap = run_regression(cases(), lane='llm')
    for seed_snap in snap['seeds'].values():
        for etype, row in seed_snap.items():
            assert row['detected'] == row['applicable']
            assert row['not_detected'] == 0
            assert row['false_flags'] == 0


def test_llm_lane_differs_from_baseline_guard_only_in_numbers():
    batch = cases()
    base = run_regression(batch)
    llm = run_regression(batch, lane='llm')
    assert check_snapshot(llm, copy.deepcopy(llm)) == []
    assert llm != base or base['seeds']['0']['upcoding']['detected'] == \
        base['seeds']['0']['upcoding']['applicable']


def test_committed_llm_snapshot_matches_live():
    live = run_regression(cases(), lane='llm')
    expected = json.loads(SNAPSHOT.read_text())
    assert check_snapshot(live, expected) == []
