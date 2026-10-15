import copy
import random

import pytest

from medcode_audit.goldset import build_gold_cases, make_assertion_case
from medcode_audit.schema import parse_case

CODES = ('E11.9', 'I10', 'J45.30', 'N18.31', 'D50.9')
PHRASES = (
    'type 2 diabetes without complications', 'essential hypertension',
    'mild persistent asthma, uncomplicated', 'chronic kidney disease stage 3a',
    'iron deficiency anemia, unspecified',
)


@pytest.mark.parametrize('code,phrase', zip(CODES, PHRASES))
@pytest.mark.parametrize('status,prefix', [
    ('affirmed', 'Confirmed diagnosis: '),
    ('negated', 'Condition explicitly absent: '),
    ('uncertain', 'Possible diagnosis, not confirmed: '),
])
def test_separate_assertion_rules(code, phrase, status, prefix):
    case = make_assertion_case('test-1', [(code, status)])
    sentence = prefix + phrase + '.'
    assert case['note_text'] == 'SYNTHETIC NOTE. Assertion exercise. ' + sentence
    assert case['gold_codes'] == ([{'code': code, 'evidence_quote': sentence}]
                                  if status == 'affirmed' else [])
    assert parse_case(case).synthetic is True
    assert case['injected_errors'] == []


def test_mixed_note_scope_and_order():
    source = [('I10', 'negated'), ('E11.9', 'affirmed'),
              ('D50.9', 'uncertain'), ('N18.31', 'affirmed')]
    saved = copy.deepcopy(source)
    case = make_assertion_case('mixed', source)
    assert source == saved
    assert [g['code'] for g in case['gold_codes']] == ['E11.9', 'N18.31']
    assert all(g['evidence_quote'].startswith('Confirmed diagnosis: ')
               and g['evidence_quote'] in case['note_text'] for g in case['gold_codes'])


@pytest.mark.parametrize('assertions', [
    [], None, 'I10', [('X00', 'affirmed')], [('I10', 'possible')],
    [('I10',)], [('I10', 'affirmed', 'extra')], [None],
    [('I10', 'affirmed'), ('I10', 'affirmed')],
    [('I10', 'affirmed'), ('I10', 'negated')], [([], 'affirmed')],
])
def test_reject_invalid_or_contradictory_assertions(assertions):
    with pytest.raises(ValueError, match='assertions'):
        make_assertion_case('test', assertions)


@pytest.mark.parametrize('case_id', ['', '  ', None, 7, True])
def test_reject_invalid_case_id(case_id):
    with pytest.raises(ValueError, match='case_id'):
        make_assertion_case(case_id, [('I10', 'affirmed')])


def test_batch_count_distinct_notes_ids_and_schema():
    batch = build_gold_cases()
    assert len(batch) == 37
    assert [c['id'] for c in batch] == [f'gen-{n:03d}' for n in range(14, 51)]
    assert len({c['note_text'] for c in batch}) == 37
    assert all(parse_case(c).synthetic for c in batch)
    assert {len(c['gold_codes']) for c in batch} == {0, 1, 2}


def test_batch_coverage_independent_of_implementation_labels():
    batch = build_gold_cases()
    for index, code in enumerate(CODES):
        assert [g['code'] for g in batch[index]['gold_codes']] == [code]
        assert batch[5 + index]['gold_codes'] == []
        assert batch[10 + index]['gold_codes'] == []
        assert [g['code'] for g in batch[15 + index]['gold_codes']] == [code]
        assert [g['code'] for g in batch[20 + index]['gold_codes']] == [code]
        assert [g['code'] for g in batch[25 + index]['gold_codes']] == [code]
        assert [g['code'] for g in batch[30 + index]['gold_codes']] == [
            code, CODES[(index + 1) % 5]]
    assert batch[35]['gold_codes'] == batch[36]['gold_codes'] == []


def test_reproducibility_rng_and_independent_records():
    before = random.getstate()
    batch = build_gold_cases()
    assert random.getstate() == before
    assert batch == build_gold_cases()
    saved = copy.deepcopy(batch[15])
    batch[0]['gold_codes'][0]['code'] = 'X00'
    batch[0]['injected_errors'].append('wrong_code')
    assert batch[15] == saved
    assert build_gold_cases()[15] == saved
    assert build_gold_cases()[0]['gold_codes'][0]['code'] == 'E11.9'


def test_custom_id_range():
    assert build_gold_cases(1000)[-1]['id'] == 'gen-1036'


@pytest.mark.parametrize('start_id', [0, -1, True, False, 1.5, '14', None])
def test_invalid_start_id(start_id):
    with pytest.raises(ValueError, match='start_id'):
        build_gold_cases(start_id)
