import copy
import random

import pytest

from medcode_audit.generator import generate_cases
from medcode_audit.schema import parse_case


def test_repeatable_seed_and_ids():
    first = generate_cases(10, seed=42)
    assert first == generate_cases(10, seed=42)
    assert [c['id'] for c in first] == [f'gen-{n:03d}' for n in range(4, 14)]


def test_valid_synthetic_cases_and_verbatim_evidence():
    for raw in generate_cases(25, seed=7):
        case = parse_case(raw)
        assert case.synthetic is True
        assert case.note_text.startswith('SYNTHETIC NOTE.')
        assert case.injected_errors == []
        assert len(case.gold_codes) == 1
        assert case.gold_codes[0].evidence_quote in case.note_text


def test_five_conditions_covered_in_each_cycle():
    cases = generate_cases(10)
    for start in (0, 5):
        assert {c['gold_codes'][0]['code'] for c in cases[start:start+5]} == {
            'E11.9', 'I10', 'J45.30', 'N18.31', 'D50.9'
        }


def test_notes_use_only_closed_non_identifying_vocabulary():
    quotes = {
        'type 2 diabetes without complications', 'essential hypertension',
        'mild persistent asthma, uncomplicated', 'chronic kidney disease stage 3a',
        'iron deficiency anemia, unspecified',
    }
    wrappers = {
        ('SYNTHETIC NOTE. Assessment: ', '. Routine follow-up.'),
        ('SYNTHETIC NOTE. Documented diagnosis: ', '. Review visit.'),
        ('SYNTHETIC NOTE. Active condition: ', '. Follow-up assessment.'),
    }
    for case in generate_cases(100, seed=42):
        quote = case['gold_codes'][0]['evidence_quote']
        assert quote in quotes
        assert any(case['note_text'] == a + quote + b for a, b in wrappers)


def test_rng_state_untouched():
    before = random.getstate()
    generate_cases(10, seed=99)
    assert random.getstate() == before


def test_independent_mutable_records():
    cases = generate_cases(10)
    saved = copy.deepcopy(cases[5])
    cases[0]['gold_codes'][0]['code'] = 'X00'
    cases[0]['injected_errors'].append('wrong_code')
    assert cases[5] == saved
    assert generate_cases(10)[5] == saved


def test_zero_and_custom_start_id():
    assert generate_cases(0) == []
    assert [c['id'] for c in generate_cases(2, start_id=1000)] == ['gen-1000', 'gen-1001']


@pytest.mark.parametrize('argument,bad', [
    ('count', -1), ('count', True), ('count', 1.5), ('count', '10'),
    ('seed', True), ('seed', None), ('seed', 1.5),
    ('start_id', 0), ('start_id', -1), ('start_id', False), ('start_id', '4'),
])
def test_rejects_bad_arguments(argument, bad):
    with pytest.raises(ValueError, match=argument):
        generate_cases(**{argument: bad})
