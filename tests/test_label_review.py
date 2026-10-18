import copy
import json
from pathlib import Path

import pytest

from medcode_audit.goldset import build_gold_cases
from medcode_audit.review import (MARKS, SHEET_NAME, SHEET_VERSION,
                                  build_review_sheet, dump_sheet, load_sheet,
                                  sample_cases, stratum_key, summarize_review)

ROOT = Path(__file__).resolve().parents[1]

AFF = 'SYNTHETIC NOTE. Assertion exercise. Confirmed diagnosis: asthma.'
NEG = 'SYNTHETIC NOTE. Assertion exercise. Condition explicitly absent: asthma.'
UNC = 'SYNTHETIC NOTE. Assertion exercise. Possible diagnosis, not confirmed: asthma.'
MIX = ('SYNTHETIC NOTE. Assertion exercise. Confirmed diagnosis: asthma. '
       'Condition explicitly absent: essential hypertension.')
PROSE = 'SYNTHETIC NOTE. 58-year-old with type 2 diabetes without complications.'


def case(cid, note, gold=None):
    return {'id': cid, 'synthetic': True, 'note_text': note,
            'gold_codes': gold or [], 'injected_errors': []}


def gold(code, quote):
    return {'code': code, 'evidence_quote': quote}


def prose_cases(prefix, count):
    return [case(f'{prefix}-{i:03d}', PROSE) for i in range(count)]


def test_marks_and_sheet_identity():
    assert MARKS == ('agree', 'disagree')
    assert SHEET_VERSION == 1
    assert isinstance(SHEET_NAME, str) and SHEET_NAME


def test_stratum_from_closed_sentence_markers():
    assert stratum_key(case('t', AFF)) == 'A'
    assert stratum_key(case('t', NEG)) == 'N'
    assert stratum_key(case('t', UNC)) == 'U'
    assert stratum_key(case('t', MIX)) == 'AN'
    assert stratum_key(case('t', AFF + ' ' + UNC)) == 'AU'
    assert stratum_key(case('t', PROSE)) == 'none'


def test_sample_is_deterministic_and_within_bounds():
    cases = build_gold_cases(14)
    first = sample_cases(cases, 10, seed=0)
    assert first == sample_cases(cases, 10, seed=0)
    assert len(first) == 10
    assert len({c['id'] for c in first}) == 10
    assert all(c in cases for c in first)


def test_sample_seed_rotates_within_stratum():
    cases = prose_cases('c', 5)
    assert [c['id'] for c in sample_cases(cases, 3, seed=0)] == ['c-000', 'c-001', 'c-002']
    assert [c['id'] for c in sample_cases(cases, 3, seed=1)] == ['c-001', 'c-002', 'c-003']


def test_sample_covers_every_stratum():
    cases = build_gold_cases(14)
    sample = sample_cases(cases, 10, seed=0)
    assert {stratum_key(c) for c in sample} == {'A', 'AN', 'AU', 'N', 'U'}


def test_sample_covers_all_six_strata_of_checked_in_set():
    path = ROOT / 'data' / 'synthetic'
    cases = [json.loads(p.read_text()) for p in sorted(path.glob('*.json'))]
    assert len(cases) == 50
    sample = sample_cases(cases, 12, seed=42)
    assert len(sample) == 12
    assert {stratum_key(c) for c in sample} == {'A', 'AN', 'AU', 'N', 'U', 'none'}


def test_sample_input_validation():
    cases = prose_cases('c', 3)
    with pytest.raises(ValueError):
        sample_cases('not a list', 1)
    with pytest.raises(ValueError):
        sample_cases(cases + [cases[0]], 1)  # duplicate id
    for bad_case in ({'id': 'x'}, {'id': '', 'note_text': 'n'},
                     {'id': 'x', 'note_text': 5}, 'not a dict'):
        with pytest.raises(ValueError):
            sample_cases([bad_case], 1)
    for bad_size in (0, 4, True, 1.5, '2'):
        with pytest.raises(ValueError):
            sample_cases(cases, bad_size)
    for bad_seed in (True, 1.5, '0', None):
        with pytest.raises(ValueError):
            sample_cases(cases, 1, seed=bad_seed)


def test_inputs_are_never_mutated():
    cases = build_gold_cases(14)[:8] + [case('ctrl', PROSE)]
    snapshot = copy.deepcopy(cases)
    sample_cases(cases, 4, seed=3)
    build_review_sheet(cases)
    assert cases == snapshot


def test_sheet_rows_follow_gold_order_with_reviewer_defaults():
    c = case('t-1', AFF, [gold('J45.909', 'Confirmed diagnosis: asthma.'),
                          gold('I10', 'Essential hypertension')])
    sheet = build_review_sheet([c])
    assert [r['gold_code'] for r in sheet['rows']] == ['J45.909', 'I10']
    row = sheet['rows'][0]
    assert row == {'case_id': 't-1', 'gold_code': 'J45.909',
                   'evidence_quote': 'Confirmed diagnosis: asthma.',
                   'reviewer_mark': None, 'reviewer_note': ''}


def test_empty_gold_case_gets_one_control_row():
    sheet = build_review_sheet([case('ctrl', NEG)])
    assert sheet['rows'] == [{'case_id': 'ctrl', 'gold_code': None,
                              'evidence_quote': None, 'reviewer_mark': None,
                              'reviewer_note': ''}]


def test_sheet_header_and_bad_gold_shape():
    sheet = build_review_sheet([case('t', AFF, [gold('I10', 'q')])])
    assert sheet['sheet'] == SHEET_NAME
    assert sheet['version'] == 1
    assert sheet['provisional'] is True
    with pytest.raises(ValueError):
        build_review_sheet([case('bad', AFF, ['not-a-dict'])])
    with pytest.raises(ValueError):
        build_review_sheet([case('bad', AFF, [{'code': 'I10'}])])


def test_dump_load_round_trip():
    sheet = build_review_sheet([case('t-1', AFF, [gold('I10', 'q')]),
                                case('ctrl', NEG)])
    sheet['rows'][0]['reviewer_mark'] = 'agree'
    sheet['rows'][1]['reviewer_mark'] = 'disagree'
    sheet['rows'][1]['reviewer_note'] = 'absent sentence is not evidence'
    assert load_sheet(dump_sheet(sheet)) == sheet


def test_load_sheet_rejects_malformed():
    good = build_review_sheet([case('t', AFF, [gold('I10', 'q')])])
    with pytest.raises(ValueError):
        load_sheet('not json')
    with pytest.raises(ValueError):
        load_sheet(json.dumps([1, 2]))
    for mutate in (
            lambda s: s.update(version=2),
            lambda s: s.update(provisional=False),
            lambda s: s['rows'][0].update(reviewer_mark='maybe'),
            lambda s: s['rows'][0].update(reviewer_mark=1),
            lambda s: s['rows'][0].update(reviewer_note=None),
            lambda s: s['rows'][0].pop('reviewer_note'),
            lambda s: s['rows'][0].update(extra=True),
            lambda s: s['rows'][0].update(gold_code=None),
            lambda s: s['rows'][0].update(case_id='')):
        bad = copy.deepcopy(good)
        mutate(bad)
        with pytest.raises(ValueError):
            load_sheet(json.dumps(bad))


def test_summarize_counts_and_disagreement_list():
    sheet = build_review_sheet([case('t-1', AFF, [gold('I10', 'q1'), gold('E11.9', 'q2')]),
                                case('t-2', AFF, [gold('J45.909', 'q3')]),
                                case('ctrl', NEG)])
    marks = ['agree', 'disagree', 'disagree', None]
    notes = ['', 'quote truncated', 'absent sentence is not support', '']
    for row, mark, note in zip(sheet['rows'], marks, notes):
        row['reviewer_mark'] = mark
        row['reviewer_note'] = note
    summary = summarize_review(sheet)
    assert summary['total_rows'] == 4
    assert summary['reviewed'] == 3
    assert summary['unreviewed'] == 1
    assert summary['agree'] == 1
    assert summary['disagree'] == 2
    assert summary['disagreements'] == [
        {'case_id': 't-1', 'gold_code': 'E11.9', 'reviewer_note': 'quote truncated'},
        {'case_id': 't-2', 'gold_code': 'J45.909',
         'reviewer_note': 'absent sentence is not support'}]


def test_summarize_unreviewed_sheet_and_validation():
    sheet = build_review_sheet([case('t', AFF, [gold('I10', 'q')]), case('c', NEG)])
    summary = summarize_review(sheet)
    assert summary['reviewed'] == 0
    assert summary['unreviewed'] == 2
    assert summary['disagreements'] == []
    with pytest.raises(ValueError):
        summarize_review({'sheet': 'wrong'})
