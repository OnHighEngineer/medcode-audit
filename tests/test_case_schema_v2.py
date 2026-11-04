"""Frozen tests for spec 020: case schema v2 (optional procedure codes).

All procedure codes here are clearly synthetic placeholders that match no
real code set; the vocabulary decision for case data is pending.
"""
import pytest

from medcode_audit.schema import Case, CaseValidationError, parse_case

NOTE = 'SYNTHETIC NOTE. Patient had the placeholder scan today.'


def v1_case():
    return {'id': 'syn-v1', 'synthetic': True, 'note_text': NOTE,
            'gold_codes': [], 'injected_errors': []}


def v2_case(codes):
    c = v1_case()
    c['procedure_codes'] = codes
    return c


def test_v1_case_parses_with_empty_procedure_codes():
    case = parse_case(v1_case())
    assert case.procedure_codes == []


def test_v2_case_parses_procedure_codes():
    case = parse_case(v2_case([{'code': 'PX001', 'evidence_quote': 'placeholder scan'}]))
    assert [(p.code, p.evidence_quote) for p in case.procedure_codes] == [
        ('PX001', 'placeholder scan')]


@pytest.mark.parametrize('code', ['PX001', 'A0000', '00000', 'ZZ9ZA', 'AB12'])
def test_generic_shape_accepts_cpt_hcpcs_and_placeholders(code):
    case = parse_case(v2_case([{'code': code, 'evidence_quote': 'placeholder scan'}]))
    assert case.procedure_codes[0].code == code


@pytest.mark.parametrize('code', ['PX1', 'TOOLONG99', 'px001', 'PX-001', ''])
def test_generic_shape_rejects_bad_codes(code):
    with pytest.raises(CaseValidationError):
        parse_case(v2_case([{'code': code, 'evidence_quote': 'placeholder scan'}]))


@pytest.mark.parametrize('codes', [
    'not a list',
    [{'evidence_quote': 'placeholder scan'}],
    [{'code': 'PX001'}],
    [{'code': 'PX001', 'evidence_quote': ''}],
    [{'code': 'PX001', 'evidence_quote': 'text not in the note'}],
    [{'code': 123, 'evidence_quote': 'placeholder scan'}],
    ['just a string'],
])
def test_malformed_procedure_codes_rejected(codes):
    with pytest.raises(CaseValidationError):
        parse_case(v2_case(codes))


def test_case_dataclass_default_keeps_positional_construction():
    case = Case('syn-x', True, NOTE, [], [])
    assert case.procedure_codes == []
