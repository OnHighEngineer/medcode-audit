import copy

import pytest

from medcode_audit.auditor_schema import validate_auditor_output
from medcode_audit.evidence import (VERIFICATION_STATUSES, find_span,
                                    verification_summary, verify_evidence,
                                    verify_verdict)

NOTE = 'SYNTHETIC NOTE. 61-year-old with essential hypertension, on lisinopril.'


def vd(code, verdict, quote=None):
    d = {'code': code, 'verdict': verdict}
    if quote is not None:
        d['evidence_quote'] = quote
    return d


def test_status_vocabulary_is_closed():
    assert VERIFICATION_STATUSES == ('verified', 'unverified', 'invalid',
                                     'not_applicable')


def test_find_span_offsets_and_absence():
    assert find_span(NOTE, 'essential hypertension') == (33, 55)
    assert find_span(NOTE, 'NOTE') == (10, 14)
    assert find_span(NOTE, 'diabetes') is None
    assert find_span(NOTE, 'Essential Hypertension') is None  # case-sensitive


def test_find_span_validates_inputs():
    for bad_note, bad_quote in ((5, 'x'), (NOTE, ''), (NOTE, 5), (None, 'x')):
        with pytest.raises(ValueError):
            find_span(bad_note, bad_quote)


def test_supported_with_verbatim_quote_is_verified_with_span():
    rec = verify_verdict(vd('I10', 'SUPPORTED', 'essential hypertension'), NOTE)
    assert rec == {'code': 'I10', 'verdict': 'SUPPORTED', 'status': 'verified',
                   'span': (33, 55)}


def test_supported_without_quote_is_unverified():
    rec = verify_verdict(vd('I10', 'SUPPORTED'), NOTE)
    assert rec['status'] == 'unverified'
    assert rec['span'] is None


def test_non_verbatim_quote_is_invalid_for_any_verdict():
    for verdict in ('SUPPORTED', 'UNSUPPORTED', 'WRONG_SPECIFICITY', 'MISSED'):
        rec = verify_verdict(vd('I10', verdict, 'not in the note'), NOTE)
        assert rec['status'] == 'invalid'
        assert rec['span'] is None


def test_non_supported_quote_rules():
    rec = verify_verdict(vd('I10', 'UNSUPPORTED', 'on lisinopril'), NOTE)
    assert rec['status'] == 'verified'
    assert rec['span'] == (57, 70)
    rec = verify_verdict(vd('I10', 'UNSUPPORTED'), NOTE)
    assert rec['status'] == 'not_applicable'
    rec = verify_verdict(vd('I10', 'MISSED'), NOTE)
    assert rec['status'] == 'not_applicable'


def test_verify_verdict_validates_inputs():
    with pytest.raises(ValueError):
        verify_verdict('not-a-dict', NOTE)
    with pytest.raises(ValueError):
        verify_verdict(vd('I10', 'MAYBE'), NOTE)
    with pytest.raises(ValueError):
        verify_verdict(vd('I10', 'SUPPORTED'), 5)


def test_verify_evidence_batch_order_and_validation():
    verdicts = [vd('I10', 'SUPPORTED', 'essential hypertension'),
                vd('E11.9', 'SUPPORTED'),
                vd('J45.30', 'UNSUPPORTED')]
    records = verify_evidence(verdicts, NOTE)
    assert [r['status'] for r in records] == ['verified', 'unverified',
                                              'not_applicable']
    assert [r['code'] for r in records] == ['I10', 'E11.9', 'J45.30']
    with pytest.raises(ValueError):
        verify_evidence('not-a-list', NOTE)


def test_verification_summary_zero_fills():
    records = verify_evidence([vd('I10', 'SUPPORTED', 'essential hypertension'),
                               vd('E11.9', 'SUPPORTED'),
                               vd('J45.30', 'UNSUPPORTED', 'bogus'),
                               vd('D50.9', 'MISSED')], NOTE)
    assert verification_summary(records) == {
        'total': 4, 'verified': 1, 'unverified': 1, 'invalid': 1,
        'not_applicable': 1}
    assert verification_summary([]) == {
        'total': 0, 'verified': 0, 'unverified': 0, 'invalid': 0,
        'not_applicable': 0}


def test_inputs_not_mutated():
    verdict = vd('I10', 'SUPPORTED', 'essential hypertension')
    snapshot = copy.deepcopy(verdict)
    verify_verdict(verdict, NOTE)
    verify_evidence([verdict], NOTE)
    assert verdict == snapshot


def test_schema_validator_uses_the_same_verbatim_rule():
    good = {'verdicts': [vd('I10', 'SUPPORTED', 'essential hypertension')],
            'missed_codes': []}
    assert validate_auditor_output(good, ['I10'], note_text=NOTE)
    bad = {'verdicts': [vd('I10', 'SUPPORTED', 'not in the note')],
           'missed_codes': []}
    with pytest.raises(ValueError):
        validate_auditor_output(bad, ['I10'], note_text=NOTE)
