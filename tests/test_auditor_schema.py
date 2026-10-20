import copy

import pytest

from medcode_audit.auditor_schema import VERDICTS, validate_auditor_output
from medcode_audit.goldset import build_gold_cases
from medcode_audit.runner import run_eval

NOTE = 'SYNTHETIC NOTE. 61-year-old with essential hypertension, on lisinopril.'


def out(verdicts, missed=None):
    return {'verdicts': verdicts, 'missed_codes': missed or []}


def v(code, verdict, quote=None):
    d = {'code': code, 'verdict': verdict}
    if quote is not None:
        d['evidence_quote'] = quote
    return d


def test_verdict_names_constant():
    assert VERDICTS == ('SUPPORTED', 'UNSUPPORTED', 'WRONG_SPECIFICITY', 'MISSED')


def test_valid_minimal_output_is_normalized():
    result = validate_auditor_output(out([v('I10', 'SUPPORTED')]), ['I10'])
    assert result == {'verdicts': [{'code': 'I10', 'verdict': 'SUPPORTED'}],
                      'missed_codes': []}


def test_output_must_be_a_dict_with_two_lists():
    for bad in ('x', [], None, out('not-a-list'), {'verdicts': []},
                {'missed_codes': []}):
        with pytest.raises(ValueError):
            validate_auditor_output(bad, ['I10'])


def test_unknown_verdict_and_bad_verdict_shape():
    with pytest.raises(ValueError):
        validate_auditor_output(out([v('I10', 'MAYBE')]), ['I10'])
    with pytest.raises(ValueError):
        validate_auditor_output(out([{'code': 'I10'}]), ['I10'])
    with pytest.raises(ValueError):
        validate_auditor_output(out([{'verdict': 'SUPPORTED'}]), ['I10'])
    with pytest.raises(ValueError):
        validate_auditor_output(out(['not-a-dict']), ['I10'])


def test_duplicate_and_coverage_errors():
    with pytest.raises(ValueError):
        validate_auditor_output(
            out([v('I10', 'SUPPORTED'), v('I10', 'UNSUPPORTED')]), ['I10'])
    with pytest.raises(ValueError):  # missing claim
        validate_auditor_output(out([v('I10', 'SUPPORTED')]), ['I10', 'E11.9'])
    with pytest.raises(ValueError):  # extra code
        validate_auditor_output(
            out([v('I10', 'SUPPORTED'), v('E11.9', 'SUPPORTED')]), ['I10'])


def test_missed_codes_and_claimed_codes_are_validated():
    with pytest.raises(ValueError):
        validate_auditor_output(out([v('I10', 'SUPPORTED')], ['I10', 5]), ['I10'])
    with pytest.raises(ValueError):
        validate_auditor_output(out([v('I10', 'SUPPORTED')], 'I10'), ['I10'])
    for bad_claimed in ('I10', ['I10', 5], None):
        with pytest.raises(ValueError):
            validate_auditor_output(out([v('I10', 'SUPPORTED')]), bad_claimed)


def test_evidence_quote_optional_and_preserved():
    result = validate_auditor_output(
        out([v('I10', 'SUPPORTED', 'essential hypertension')]), ['I10'])
    assert result['verdicts'][0]['evidence_quote'] == 'essential hypertension'


def test_evidence_quote_must_be_a_nonempty_string():
    for bad in ('', 5, ['x']):
        with pytest.raises(ValueError):
            validate_auditor_output(out([v('I10', 'SUPPORTED', bad)]), ['I10'])


def test_evidence_verbatim_check_runs_when_note_given():
    good = out([v('I10', 'SUPPORTED', 'essential hypertension')])
    assert validate_auditor_output(good, ['I10'], note_text=NOTE)
    bad = out([v('I10', 'SUPPORTED', 'Essential Hypertension')])  # case differs
    with pytest.raises(ValueError):
        validate_auditor_output(bad, ['I10'], note_text=NOTE)
    absent = out([v('I10', 'SUPPORTED', 'type 2 diabetes')])
    with pytest.raises(ValueError):
        validate_auditor_output(absent, ['I10'], note_text=NOTE)


def test_verbatim_check_skipped_without_note():
    result = validate_auditor_output(
        out([v('I10', 'SUPPORTED', 'not in any note')]), ['I10'])
    assert result['verdicts'][0]['evidence_quote'] == 'not in any note'


def test_input_not_mutated_and_result_is_a_copy():
    original = out([v('I10', 'UNSUPPORTED', 'q')], ['E11.9'])
    snapshot = copy.deepcopy(original)
    result = validate_auditor_output(original, ['I10'])
    assert original == snapshot
    result['verdicts'][0]['verdict'] = 'SUPPORTED'
    result['missed_codes'].append('X')
    assert original == snapshot


def test_runner_checks_volunteered_evidence_against_the_note():
    cases = build_gold_cases(14)[:1]

    def bad_evidence_auditor(note, claimed):
        return {'verdicts': [{'code': c, 'verdict': 'SUPPORTED',
                              'evidence_quote': 'this string is not in the note'}
                             for c in claimed],
                'missed_codes': []}

    with pytest.raises(ValueError):
        run_eval(cases, bad_evidence_auditor, error_types=('unsupported_code',))

    def good_auditor(note, claimed):
        return {'verdicts': [{'code': c, 'verdict': 'SUPPORTED'} for c in claimed],
                'missed_codes': []}

    run = run_eval(cases, good_auditor, error_types=('unsupported_code',))
    assert run['tally']['unsupported_code']['applicable'] == 1
