"""Frozen tests for spec 015 (ordinal upcoding). Written before the module."""
import pytest

from medcode_audit.code_lookup import lookup
from medcode_audit.upcoding import assess_upcoding

NOTE_CKD3A = ('Confirmed diagnosis: chronic kidney disease stage 3a. '
              'Monitoring continues.')
NOTE_ASTHMA = ('Confirmed diagnosis: mild persistent asthma, uncomplicated. '
               'Inhaler continued.')
NOTE_NEGATED = 'Condition explicitly absent: chronic kidney disease stage 3a.'
NOTE_DM = 'Confirmed diagnosis: type 2 diabetes without complications.'


def test_ranks_pinned_to_titles():
    assert lookup('N18.1')['rank'] == 1 and 'stage 1' in lookup('N18.1')['description']
    assert lookup('N18.2')['rank'] == 2 and 'stage 2' in lookup('N18.2')['description']
    assert lookup('N18.31')['rank'] == 3 and 'stage 3a' in lookup('N18.31')['description']
    assert lookup('N18.32')['rank'] == 4 and 'stage 3b' in lookup('N18.32')['description']
    assert lookup('N18.4')['rank'] == 5 and 'stage 4' in lookup('N18.4')['description']
    assert lookup('N18.5')['rank'] == 6 and 'stage 5' in lookup('N18.5')['description']
    assert lookup('J45.20')['rank'] == 1 and 'Mild intermittent' in lookup('J45.20')['description']
    assert lookup('J45.30')['rank'] == 2 and 'Mild persistent' in lookup('J45.30')['description']
    assert lookup('J45.40')['rank'] == 3 and 'Moderate persistent' in lookup('J45.40')['description']
    assert lookup('J45.50')['rank'] == 4 and 'Severe persistent' in lookup('J45.50')['description']


def test_unranked_codes():
    assert lookup('N18.9')['rank'] is None
    assert lookup('E11.9')['rank'] is None
    assert lookup('I10')['rank'] is None
    assert lookup('D50.9')['rank'] is None


def test_higher_stage_claimed_than_supported_fires():
    findings = assess_upcoding(NOTE_CKD3A, ['N18.32'])
    assert len(findings) == 1
    f = findings[0]
    assert f['code'] == 'N18.32'
    assert f['supported_code'] == 'N18.31'
    assert f['claimed_rank'] == 4
    assert f['supported_rank'] == 3
    start, end = f['span']
    assert NOTE_CKD3A[start:end] == f['evidence_quote']


def test_much_higher_stage_also_fires():
    assert [f['code'] for f in assess_upcoding(NOTE_CKD3A, ['N18.5'])] == ['N18.5']


def test_asthma_severity_upcoding_fires():
    findings = assess_upcoding(NOTE_ASTHMA, ['J45.50'])
    assert [f['code'] for f in findings] == ['J45.50']
    assert findings[0]['claimed_rank'] == 4
    assert findings[0]['supported_rank'] == 2


@pytest.mark.parametrize('note,codes', [
    (NOTE_CKD3A, ['N18.31']),      # same rank
    (NOTE_CKD3A, ['N18.2']),       # lower rank (downcoding, not today)
    (NOTE_CKD3A, ['N18.9']),       # unspecified, never assessed
    (NOTE_CKD3A, ['E11.9']),       # different, non-ordinal family
    (NOTE_NEGATED, ['N18.5']),     # negated evidence supports nothing
    (NOTE_DM, ['N18.5']),          # unrelated affirmed condition
    (NOTE_ASTHMA, ['J45.20']),     # lower severity
])
def test_no_finding_cases(note, codes):
    assert assess_upcoding(note, codes) == []


def test_uncertain_note_supports_nothing():
    note = 'Possible diagnosis, not confirmed: chronic kidney disease stage 3a.'
    assert assess_upcoding(note, ['N18.5']) == []


@pytest.mark.parametrize('note,codes', [(None, ['N18.5']), (NOTE_CKD3A, 'N18.5'),
                                        (NOTE_CKD3A, ['N18.5', 4]), (3, ['N18.5'])])
def test_input_type_checks(note, codes):
    with pytest.raises(ValueError):
        assess_upcoding(note, codes)
