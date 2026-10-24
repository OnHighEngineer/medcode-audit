import copy

import pytest

from medcode_audit.assertions import (ASSERTION_STATUSES, detect_assertions,
                                      status_for)
from medcode_audit.baseline import audit_baseline
from medcode_audit.evidence import find_span

NOTE_AFF = 'SYNTHETIC NOTE. Assertion exercise. Confirmed diagnosis: essential hypertension.'
NOTE_NEG = 'SYNTHETIC NOTE. Assertion exercise. Condition explicitly absent: essential hypertension.'
NOTE_UNC = 'SYNTHETIC NOTE. Assertion exercise. Possible diagnosis, not confirmed: essential hypertension.'
PROSE = 'SYNTHETIC NOTE. 58-year-old with type 2 diabetes without complications. Essential hypertension, BP 128/80.'


def test_status_vocabulary_is_closed():
    assert ASSERTION_STATUSES == ('affirmed', 'negated', 'uncertain',
                                  'mentioned', 'absent', 'conflict')


def test_affirmed_closed_sentence():
    rec = status_for(NOTE_AFF, 'I10')
    assert rec['status'] == 'affirmed'
    assert rec['quote'] == 'Confirmed diagnosis: essential hypertension.'
    assert rec['span'] == find_span(NOTE_AFF, rec['quote'])
    assert 'conflicting' not in rec


def test_negated_and_uncertain_closed_sentences():
    neg = status_for(NOTE_NEG, 'I10')
    assert neg['status'] == 'negated'
    assert neg['quote'] == 'Condition explicitly absent: essential hypertension.'
    unc = status_for(NOTE_UNC, 'I10')
    assert unc['status'] == 'uncertain'
    assert unc['quote'] == 'Possible diagnosis, not confirmed: essential hypertension.'


def test_prose_mention_is_mentioned_with_verbatim_quote():
    rec = status_for(PROSE, 'I10')
    assert rec['status'] == 'mentioned'
    assert rec['quote'] == 'Essential hypertension'
    start, end = rec['span']
    assert PROSE[start:end] == 'Essential hypertension'


def test_stem_only_mention_and_absent():
    rec = status_for('SYNTHETIC NOTE. Patient is diabetic.', 'E11.9')
    assert rec['status'] == 'mentioned'
    assert rec['quote'] == 'diabet'
    rec = status_for('SYNTHETIC NOTE. Routine visit.', 'I10')
    assert rec == {'code': 'I10', 'status': 'absent', 'quote': None, 'span': None}


def test_conflict_lists_all_matched_closed_sentences():
    note = NOTE_AFF + ' ' + NOTE_NEG
    rec = status_for(note, 'I10')
    assert rec['status'] == 'conflict'
    assert rec['quote'] is None and rec['span'] is None
    assert rec['conflicting'] == ['Confirmed diagnosis: essential hypertension.',
                                  'Condition explicitly absent: essential hypertension.']


def test_detect_assertions_covers_five_conditions_in_table_order():
    records = detect_assertions(PROSE)
    assert [r['code'] for r in records] == ['E11.9', 'I10', 'J45.30', 'N18.31', 'D50.9']
    assert records[0]['status'] == 'mentioned'
    assert records[1]['status'] == 'mentioned'
    assert [r['status'] for r in records[2:]] == ['absent'] * 3


def test_input_validation():
    with pytest.raises(ValueError):
        detect_assertions(5)
    with pytest.raises(ValueError):
        status_for(PROSE, 'A00')
    with pytest.raises(ValueError):
        status_for(5, 'I10')


def test_deterministic_and_note_not_mutated():
    note = PROSE
    snapshot = copy.deepcopy(note)
    first = detect_assertions(note)
    assert note == snapshot
    assert detect_assertions(note) == first


def test_baseline_treats_conflict_as_unsupported():
    note = NOTE_AFF + ' ' + NOTE_NEG
    verdict = {v['code']: v for v in audit_baseline(note, ['I10'])['verdicts']}['I10']
    assert verdict['verdict'] == 'UNSUPPORTED'
    assert 'evidence_quote' not in verdict


def test_baseline_unchanged_on_closed_and_prose_notes():
    verdicts = {v['code']: v for v in audit_baseline(PROSE, ['I10', 'N18.31'])['verdicts']}
    assert verdicts['I10']['verdict'] == 'SUPPORTED'
    assert verdicts['I10']['evidence_quote'] == 'Essential hypertension'
    assert verdicts['N18.31']['verdict'] == 'UNSUPPORTED'
    result = audit_baseline(NOTE_NEG, ['I10'])
    assert result['verdicts'][0]['evidence_quote'] == ('Condition explicitly absent: '
                                                       'essential hypertension.')
