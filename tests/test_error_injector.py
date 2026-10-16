import copy

import pytest

from medcode_audit.goldset import build_gold_cases, make_assertion_case
from medcode_audit.injector import inject_error
from medcode_audit.schema import ERROR_TYPES

KEYS = {'source_case_id', 'error_type', 'seed', 'applicable', 'reason',
        'claimed_codes', 'injection', 'expected_findings'}


def case(assertions, cid='t-1'):
    return make_assertion_case(cid, assertions)


def test_unknown_type_and_bad_inputs():
    c = case([('I10', 'affirmed')])
    with pytest.raises(ValueError):
        inject_error(c, 'nonsense')
    for bad in (True, 1.5, '1', None):
        with pytest.raises(ValueError):
            inject_error(c, 'missed_code', seed=bad)
    with pytest.raises(ValueError):
        inject_error('not a dict', 'missed_code')


@pytest.mark.parametrize('etype', ERROR_TYPES)
def test_source_case_not_mutated_and_shape(etype):
    c = case([('I10', 'affirmed'), ('E11.9', 'negated')])
    before = copy.deepcopy(c)
    r = inject_error(c, etype, seed=3)
    assert c == before
    assert set(r) == KEYS
    assert r['source_case_id'] == 't-1' and r['error_type'] == etype
    assert r['seed'] == 3


def test_missed_code_exact():
    c = case([('E11.9', 'affirmed'), ('I10', 'affirmed')])
    r0 = inject_error(c, 'missed_code', seed=0)
    assert r0['applicable'] is True and r0['reason'] is None
    assert r0['claimed_codes'] == [{'code': 'I10', 'origin': 'gold'}]
    assert r0['injection'] == {'code': 'E11.9', 'action': 'removed'}
    assert r0['expected_findings'] == [{'code': 'E11.9', 'finding': 'missed'}]
    r1 = inject_error(c, 'missed_code', seed=1)
    assert r1['claimed_codes'] == [{'code': 'E11.9', 'origin': 'gold'}]
    assert inject_error(c, 'missed_code', seed=2)['claimed_codes'] == r0['claimed_codes']
    assert c['gold_codes'][0]['code'] == 'E11.9' and len(c['gold_codes']) == 2


def test_missed_code_empty_gold_inapplicable():
    c = case([('I10', 'negated')])
    r = inject_error(c, 'missed_code')
    assert r['applicable'] is False and r['reason'] == 'no_gold_code'
    assert r['claimed_codes'] is None and r['injection'] is None
    assert r['expected_findings'] == []


def test_unsupported_code_exact_and_separation():
    c = case([('I10', 'affirmed')])
    r = inject_error(c, 'unsupported_code', seed=0)
    assert r['claimed_codes'] == [{'code': 'I10', 'origin': 'gold'},
                                  {'code': 'E11.9', 'origin': 'injected'}]
    assert r['injection'] == {'code': 'E11.9', 'action': 'added'}
    assert r['expected_findings'] == [{'code': 'E11.9', 'finding': 'unsupported'}]
    assert [g['code'] for g in c['gold_codes']] == ['I10']
    r3 = inject_error(c, 'unsupported_code', seed=3)
    assert r3['injection']['code'] == 'D50.9'
    assert (inject_error(c, 'unsupported_code', seed=7)['injection']
            == r3['injection'])


def test_unsupported_skips_mentioned_conditions():
    c = case([('I10', 'affirmed'), ('E11.9', 'negated'), ('J45.30', 'uncertain')])
    r = inject_error(c, 'unsupported_code', seed=0)
    assert r['injection']['code'] == 'N18.31'
    r = inject_error(c, 'unsupported_code', seed=1)
    assert r['injection']['code'] == 'D50.9'


def test_unsupported_none_available():
    c = case([(k, 'negated') for k in ('E11.9', 'I10', 'J45.30', 'N18.31', 'D50.9')])
    r = inject_error(c, 'unsupported_code')
    assert r['applicable'] is False and r['reason'] == 'no_unmentioned_condition'


def test_negated_condition_exact():
    c = case([('I10', 'affirmed'), ('E11.9', 'negated')])
    r = inject_error(c, 'negated_condition')
    assert r['claimed_codes'] == [{'code': 'I10', 'origin': 'gold'},
                                  {'code': 'E11.9', 'origin': 'injected'}]
    assert r['expected_findings'] == [{'code': 'E11.9', 'finding': 'negated_claim'}]
    assert r['injection'] == {'code': 'E11.9', 'action': 'added'}


def test_negated_requires_explicit_negation():
    for assertions in ([('I10', 'affirmed')], [('I10', 'uncertain')],
                       [('I10', 'affirmed'), ('E11.9', 'uncertain')]):
        r = inject_error(case(assertions), 'negated_condition')
        assert r['applicable'] is False and r['reason'] == 'no_negated_target'


def test_negated_works_on_empty_gold_control():
    r = inject_error(case([('J45.30', 'negated')]), 'negated_condition')
    assert r['applicable'] is True
    assert r['claimed_codes'] == [{'code': 'J45.30', 'origin': 'injected'}]


@pytest.mark.parametrize('etype', ['upcoding', 'wrong_code'])
def test_deferred_types_always_inapplicable(etype):
    for c in build_gold_cases(14):
        r = inject_error(c, etype, seed=5)
        assert r['applicable'] is False
        assert r['reason'] == 'deferred_unverified_mapping'
        assert r['claimed_codes'] is None and r['expected_findings'] == []


def test_batch_is_deterministic_and_pure():
    cases = build_gold_cases(14)
    snapshot = copy.deepcopy(cases)
    for etype in ERROR_TYPES:
        for seed in range(4):
            a = [inject_error(c, etype, seed) for c in cases]
            b = [inject_error(c, etype, seed) for c in cases]
            assert a == b
    assert cases == snapshot


def test_applicability_counts_over_37_assertion_cases():
    # by scenario: 25 have gold; 16 have a negated sentence; 35 leave a condition unmentioned
    cases = build_gold_cases(14)
    counts = {e: sum(inject_error(c, e)['applicable'] for c in cases) for e in ERROR_TYPES}
    assert counts['missed_code'] == 25
    assert counts['negated_condition'] == 16
    assert counts['upcoding'] == 0 and counts['wrong_code'] == 0
    assert counts['unsupported_code'] == 35


def test_result_does_not_alias_input():
    c = case([('I10', 'affirmed')])
    r = inject_error(c, 'missed_code')
    r['claimed_codes'].append('x')
    assert [g['code'] for g in c['gold_codes']] == ['I10']
