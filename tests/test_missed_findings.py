"""Frozen tests for spec 014 (missed-code findings). Written before the module."""
import pytest

from medcode_audit.missed import find_missed

NOTE_AFFIRMED = ('Confirmed diagnosis: type 2 diabetes without complications. '
                 'Patient is recovering well.')
NOTE_TWO = ('Confirmed diagnosis: type 2 diabetes without complications. '
            'Confirmed diagnosis: essential hypertension. Rest advised.')
NOTE_PROSE = 'The patient has a history of diabetes and smokes occasionally.'
NOTE_NEGATED = 'Condition explicitly absent: essential hypertension.'
NOTE_EMPTY = 'Routine visit, no complaints.'


def test_affirmed_unclaimed_condition_is_found_with_evidence():
    findings = find_missed(NOTE_AFFIRMED, [])
    assert len(findings) == 1
    f = findings[0]
    assert f['code'] == 'E11.9'
    assert f['evidence_quote'] == (
        'Confirmed diagnosis: type 2 diabetes without complications.')
    start, end = f['span']
    assert NOTE_AFFIRMED[start:end] == f['evidence_quote']


def test_claimed_condition_is_not_a_finding():
    assert find_missed(NOTE_AFFIRMED, ['E11.9']) == []


def test_only_unclaimed_conditions_are_found():
    findings = find_missed(NOTE_TWO, ['I10'])
    assert [f['code'] for f in findings] == ['E11.9']


def test_prose_mention_is_found_with_mention_span():
    findings = find_missed(NOTE_PROSE, [])
    assert [f['code'] for f in findings] == ['E11.9']
    f = findings[0]
    start, end = f['span']
    assert NOTE_PROSE[start:end] == f['evidence_quote']
    assert f['evidence_quote'].lower().startswith('diabet')


@pytest.mark.parametrize('note', [NOTE_NEGATED, NOTE_EMPTY])
def test_negated_and_empty_notes_have_no_findings(note):
    assert find_missed(note, []) == []


def test_uncertain_note_has_no_findings():
    note = 'Possible diagnosis, not confirmed: mild persistent asthma, uncomplicated.'
    assert find_missed(note, []) == []


@pytest.mark.parametrize('note, codes', [(None, []), (NOTE_AFFIRMED, 'E11.9'),
                                         (NOTE_AFFIRMED, ['E11.9', 7]), (5, [])])
def test_input_type_checks(note, codes):
    with pytest.raises(ValueError):
        find_missed(note, codes)


def test_findings_are_fresh_dicts():
    first = find_missed(NOTE_AFFIRMED, [])[0]
    first['code'] = 'corrupted'
    assert find_missed(NOTE_AFFIRMED, [])[0]['code'] == 'E11.9'
