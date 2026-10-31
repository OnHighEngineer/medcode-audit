"""Frozen tests for spec 017: failure analysis report."""
import copy

import pytest

from medcode_audit.failure_analysis import (analyze_run, condition_band,
                                            format_failure_analysis,
                                            make_mentioned_blind_auditor)
from medcode_audit.runner import run_eval

HEADER = ('FAILURE ANALYSIS (PROVISIONAL): synthetic labels, no clinical '
          'review yet (milestone 6). Explains where failures concentrate; '
          'counts only, not trusted scores.')


def case(cid, note, gold):
    return {'id': cid, 'synthetic': True, 'note_text': note,
            'gold_codes': [{'code': c, 'evidence_quote': q} for c, q in gold],
            'injected_errors': []}


CLOSED = ('Confirmed diagnosis: mild persistent asthma, uncomplicated. '
          'Condition explicitly absent: chronic kidney disease stage 3a.')
FREE = ('SYNTHETIC NOTE. 58-year-old with type 2 diabetes without '
        'complications, well controlled. Essential hypertension, '
        'BP 128/80.')


def cases():
    return [case('t-001', CLOSED, [('J45.30', 'mild persistent asthma, uncomplicated')]),
            case('t-002', FREE, [('E11.9', 'type 2 diabetes without complications'),
                                 ('I10', 'Essential hypertension')]),
            case('t-003', 'Condition explicitly absent: iron deficiency anemia, unspecified.', [])]


def test_condition_band_labels():
    assert condition_band(cases()[0]) == 'single_condition'
    assert condition_band(cases()[1]) == 'multi_condition'
    assert condition_band(cases()[2]) == 'no_gold'


@pytest.mark.parametrize('bad', [None, 'x', {}, {'id': 't-1'}])
def test_condition_band_rejects_malformed(bad):
    with pytest.raises(ValueError):
        condition_band(bad)


def run_row(cid, etype, status, reason=None, flags=()):
    return {'source_case_id': cid, 'error_type': etype, 'seed': 0,
            'status': status, 'reason': reason, 'expected_findings': [],
            'false_flags': list(flags)}


def tiny_run(rows):
    tally = {}
    for r in rows:
        t = tally.setdefault(r['error_type'], {'applicable': 0, 'detected': 0,
                                               'not_detected': 0, 'inapplicable': 0,
                                               'false_flags': 0, 'reasons': {}})
        t[r['status'] if r['status'] != 'inapplicable' else 'inapplicable'] += 1
    return {'provisional': True, 'seed': 0, 'results': rows, 'tally': tally}


def test_analyze_run_breaks_down_not_detected():
    rows = [run_row('t-001', 'missed_code', 'not_detected'),
            run_row('t-002', 'missed_code', 'not_detected'),
            run_row('t-003', 'missed_code', 'detected'),
            run_row('t-002', 'upcoding', 'inapplicable', reason='no_ordinal_gold_code')]
    out = analyze_run(tiny_run(rows), cases())
    assert out['provisional'] is True and out['seed'] == 0
    assert out['error_types'] == ['missed_code', 'upcoding']
    nd = out['not_detected']['missed_code']
    assert nd['total'] == 2
    assert nd['cases'] == ['t-001', 't-002']
    assert nd['by_stratum'] == {'AN': 1, 'none': 1}
    assert nd['by_band'] == {'single_condition': 1, 'multi_condition': 1}
    assert out['inapplicable']['upcoding'] == {'no_ordinal_gold_code': 1}
    assert out['not_detected']['upcoding']['total'] == 0


def test_analyze_run_breaks_down_false_flags():
    rows = [run_row('t-002', 'unsupported_code', 'detected', flags=['I10', 'E11.9']),
            run_row('t-001', 'unsupported_code', 'detected'),
            run_row('t-003', 'unsupported_code', 'detected', flags=['D50.9'])]
    out = analyze_run(tiny_run(rows), cases())
    ff = out['false_flags']['unsupported_code']
    assert ff['total'] == 3
    assert ff['by_stratum'] == {'none': 1, 'N': 1}
    assert ff['by_band'] == {'multi_condition': 1, 'no_gold': 1}
    assert ff['cases'] == [{'case_id': 't-002', 'codes': ['E11.9', 'I10']},
                           {'case_id': 't-003', 'codes': ['D50.9']}]


@pytest.mark.parametrize('run,cases_', [
    (None, []), ({}, []),
    ({'results': 'x'}, []),
    ({'results': [run_row('ghost', 'missed_code', 'detected')]},
     [case('t-1', CLOSED, [])]),
])
def test_analyze_run_rejects_bad_input(run, cases_):
    with pytest.raises(ValueError):
        analyze_run(run, cases_)


def test_format_is_deterministic_and_complete():
    rows = [run_row('t-002', 'missed_code', 'not_detected'),
            run_row('t-001', 'missed_code', 'not_detected'),
            run_row('t-002', 'unsupported_code', 'detected', flags=['I10']),
            run_row('t-003', 'upcoding', 'inapplicable', reason='no_ordinal_gold_code')]
    run = tiny_run(rows)
    a = format_failure_analysis(analyze_run(run, cases()))
    b = format_failure_analysis(analyze_run(copy.deepcopy(run),
                                            list(reversed(cases()))))
    assert a == b
    assert a.startswith(HEADER)
    assert '%' not in a
    assert 'missed_code' in a and 'unsupported_code' in a and 'upcoding' in a
    assert 't-001' in a and 't-002' in a
    assert 'none' in a  # empty upcoding failures say none


def test_mentioned_blind_auditor_produces_analyzable_failures():
    run = run_eval(cases(), make_mentioned_blind_auditor(),
                   error_types=('missed_code', 'unsupported_code'))
    t = run['tally']
    assert t['missed_code']['not_detected'] >= 1  # t-002's dropped mentioned gold
    assert t['unsupported_code']['false_flags'] >= 2  # t-002's mentioned gold
    report = format_failure_analysis(analyze_run(run, cases()))
    assert report.startswith(HEADER)
    assert 't-002' in report
    assert '%' not in report
