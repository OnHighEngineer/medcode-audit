"""Frozen tests for spec 016 (upcoding injection and scoring). Written first."""
import copy

import pytest

from medcode_audit.baseline import audit_baseline
from medcode_audit.goldset import build_gold_cases, make_assertion_case
from medcode_audit.injector import inject_error
from medcode_audit.runner import format_report, run_eval

NOTE_CKD3A = ('Confirmed diagnosis: chronic kidney disease stage 3a. '
              'Monitoring continues.')
QUOTE_CKD3A = 'Confirmed diagnosis: chronic kidney disease stage 3a.'


def case(assertions, cid='t-1'):
    return make_assertion_case(cid, assertions)


def test_inject_replaces_with_higher_rank_ckd():
    c = case([('N18.31', 'affirmed')])
    r = inject_error(c, 'upcoding', seed=0)
    assert r['applicable'] is True and r['reason'] is None
    assert r['claimed_codes'] == [{'code': 'N18.32', 'origin': 'injected'}]
    assert r['injection'] == {'code': 'N18.32', 'action': 'replaced',
                              'replaced_code': 'N18.31'}
    assert r['expected_findings'] == [{'code': 'N18.32', 'finding': 'upcoding'}]
    assert [inject_error(c, 'upcoding', seed=s)['injection']['code']
            for s in (0, 1, 2, 3)] == ['N18.32', 'N18.4', 'N18.5', 'N18.32']


def test_inject_replaces_with_higher_rank_asthma():
    c = case([('J45.30', 'affirmed')])
    r = inject_error(c, 'upcoding', seed=0)
    assert r['claimed_codes'] == [{'code': 'J45.40', 'origin': 'injected'}]
    assert r['injection'] == {'code': 'J45.40', 'action': 'replaced',
                              'replaced_code': 'J45.30'}
    assert [inject_error(c, 'upcoding', seed=s)['injection']['code']
            for s in (0, 1, 2)] == ['J45.40', 'J45.50', 'J45.40']


def test_inject_seed_picks_target_among_ordinal_gold():
    c = case([('N18.31', 'affirmed'), ('J45.30', 'affirmed')])
    r0 = inject_error(c, 'upcoding', seed=0)
    assert r0['claimed_codes'] == [{'code': 'N18.32', 'origin': 'injected'},
                                   {'code': 'J45.30', 'origin': 'gold'}]
    r1 = inject_error(c, 'upcoding', seed=1)
    assert r1['claimed_codes'] == [{'code': 'N18.31', 'origin': 'gold'},
                                   {'code': 'J45.50', 'origin': 'injected'}]
    assert [g['code'] for g in c['gold_codes']] == ['N18.31', 'J45.30']


def test_inject_inapplicable_without_ordinal_gold():
    c = case([('E11.9', 'affirmed'), ('I10', 'affirmed'), ('D50.9', 'affirmed')])
    r = inject_error(c, 'upcoding')
    assert r['applicable'] is False and r['reason'] == 'no_ordinal_gold_code'
    assert r['claimed_codes'] is None and r['injection'] is None
    assert r['expected_findings'] == []


def test_inject_inapplicable_at_top_rank():
    for top in ('N18.5', 'J45.50'):
        raw = {'id': 't-top', 'note_text': 'SYNTHETIC NOTE.',
               'gold_codes': [{'code': top}]}
        r = inject_error(raw, 'upcoding')
        assert r['applicable'] is False and r['reason'] == 'no_higher_rank_in_family'
    raw = {'id': 't-u', 'note_text': 'SYNTHETIC NOTE.',
           'gold_codes': [{'code': 'N18.9'}]}
    assert inject_error(raw, 'upcoding')['reason'] == 'no_ordinal_gold_code'


def test_inject_deterministic_and_input_untouched():
    c = case([('N18.31', 'affirmed'), ('E11.9', 'affirmed')])
    before = copy.deepcopy(c)
    a = inject_error(c, 'upcoding', seed=4)
    assert inject_error(c, 'upcoding', seed=4) == a
    assert c == before
    assert a['claimed_codes'] == [{'code': 'N18.4', 'origin': 'injected'},
                                  {'code': 'E11.9', 'origin': 'gold'}]


def test_wrong_code_stays_deferred():
    for c in build_gold_cases(14):
        r = inject_error(c, 'wrong_code', seed=5)
        assert r['applicable'] is False
        assert r['reason'] == 'deferred_unverified_mapping'


def test_baseline_flags_upcoded_claim_with_evidence():
    out = audit_baseline(NOTE_CKD3A, ['N18.32'])
    assert out['verdicts'] == [{'code': 'N18.32', 'verdict': 'UNSUPPORTED',
                                'evidence_quote': QUOTE_CKD3A}]
    out = audit_baseline(NOTE_CKD3A, ['N18.31', 'N18.5'])
    assert out['verdicts'][0]['verdict'] == 'SUPPORTED'
    assert out['verdicts'][1] == {'code': 'N18.5', 'verdict': 'UNSUPPORTED',
                                  'evidence_quote': QUOTE_CKD3A}


def test_baseline_upcoding_needs_supported_lower_rank():
    negated = 'Condition explicitly absent: chronic kidney disease stage 3a.'
    assert audit_baseline(negated, ['N18.32'])['verdicts'] == [
        {'code': 'N18.32', 'verdict': 'UNSUPPORTED'}]
    assert audit_baseline('SYNTHETIC NOTE. Broken ankle.', ['N18.32'])['verdicts'] == [
        {'code': 'N18.32', 'verdict': 'UNSUPPORTED'}]


def test_runner_scores_upcoding_via_unsupported_verdict():
    run = run_eval(build_gold_cases(14), audit_baseline, error_types=('upcoding',))
    t = run['tally']['upcoding']
    assert t['applicable'] == 11 and t['detected'] == 11
    assert t['not_detected'] == 0 and t['false_flags'] == 0
    assert t['inapplicable'] == 26
    assert t['reasons'] == {'no_ordinal_gold_code': 26}


def test_runner_blind_auditor_misses_upcoding():
    def blind(note, claimed):
        return {'verdicts': [{'code': c, 'verdict': 'SUPPORTED'} for c in claimed],
                'missed_codes': []}
    run = run_eval(build_gold_cases(14), blind, error_types=('upcoding',))
    t = run['tally']['upcoding']
    assert t['detected'] == 0 and t['not_detected'] == 11
    assert t['false_flags'] == 0


def test_report_shows_upcoding_counts_wrong_code_still_deferred():
    run = run_eval(build_gold_cases(14), audit_baseline)
    text = format_report(run)
    assert text.splitlines()[0].startswith('PROVISIONAL')
    upcoding = [l for l in text.splitlines() if l.startswith('upcoding')][0]
    assert upcoding.startswith('upcoding: detected 11/11')
    assert 'not implemented' not in upcoding
    wrong = [l for l in text.splitlines() if l.startswith('wrong_code')][0]
    assert 'not implemented' in wrong and 'deferred_unverified_mapping' in wrong
