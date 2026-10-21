import copy

import pytest

from medcode_audit.auditor_schema import validate_auditor_output
from medcode_audit.baseline import audit_baseline
from medcode_audit.goldset import build_gold_cases
from medcode_audit.runner import run_eval

AFF_HTN = 'SYNTHETIC NOTE. Assertion exercise. Confirmed diagnosis: essential hypertension.'
NEG_HTN = 'SYNTHETIC NOTE. Assertion exercise. Condition explicitly absent: essential hypertension.'
UNC_HTN = 'SYNTHETIC NOTE. Assertion exercise. Possible diagnosis, not confirmed: essential hypertension.'
PROSE = 'SYNTHETIC NOTE. 58-year-old with type 2 diabetes without complications, well controlled. Essential hypertension, BP 128/80.'


def by_code(result):
    return {v['code']: v for v in result['verdicts']}


def test_output_always_satisfies_spec_007():
    note = AFF_HTN + ' Condition explicitly absent: mild persistent asthma, uncomplicated.'
    claimed = ['I10', 'J45.30', 'E11.9', 'A00']
    result = audit_baseline(note, claimed)
    assert validate_auditor_output(result, claimed, note_text=note) == result


def test_affirmed_closed_sentence_is_supported_with_sentence_quote():
    result = audit_baseline(AFF_HTN, ['I10'])
    verdict = by_code(result)['I10']
    assert verdict['verdict'] == 'SUPPORTED'
    assert verdict['evidence_quote'] == 'Confirmed diagnosis: essential hypertension.'


def test_negated_closed_sentence_is_unsupported_with_absent_quote():
    result = audit_baseline(NEG_HTN, ['I10'])
    verdict = by_code(result)['I10']
    assert verdict['verdict'] == 'UNSUPPORTED'
    assert verdict['evidence_quote'] == 'Condition explicitly absent: essential hypertension.'


def test_uncertain_and_absent_are_unsupported_without_quote():
    for note in (UNC_HTN, 'SYNTHETIC NOTE. Routine visit.'):
        verdict = by_code(audit_baseline(note, ['I10']))['I10']
        assert verdict['verdict'] == 'UNSUPPORTED'
        assert 'evidence_quote' not in verdict


def test_prose_mention_is_supported_with_verbatim_cased_quote():
    result = audit_baseline(PROSE, ['I10', 'E11.9'])
    verdicts = by_code(result)
    assert verdicts['I10']['verdict'] == 'SUPPORTED'
    assert verdicts['I10']['evidence_quote'] == 'Essential hypertension'
    assert verdicts['E11.9']['evidence_quote'] == 'type 2 diabetes without complications'
    for code in ('I10', 'E11.9'):
        assert verdicts[code]['evidence_quote'] in PROSE


def test_stem_only_mention_counts():
    result = audit_baseline('SYNTHETIC NOTE. Patient is diabetic.', ['E11.9'])
    assert by_code(result)['E11.9']['verdict'] == 'SUPPORTED'


def test_unknown_code_is_unsupported_without_quote():
    verdict = by_code(audit_baseline(AFF_HTN, ['A00']))['A00']
    assert verdict['verdict'] == 'UNSUPPORTED'
    assert 'evidence_quote' not in verdict


def test_missed_codes_from_affirmed_or_mentioned_conditions():
    result = audit_baseline(AFF_HTN + ' ' + PROSE, ['I10'])
    assert result['missed_codes'] == ['E11.9']
    result = audit_baseline(NEG_HTN, [])
    assert result['missed_codes'] == []
    result = audit_baseline(PROSE, [])
    assert result['missed_codes'] == ['E11.9', 'I10']


def test_empty_claimed_codes_gives_empty_verdicts():
    result = audit_baseline(AFF_HTN, [])
    assert result['verdicts'] == []
    assert result['missed_codes'] == ['I10']


def test_inputs_not_mutated_and_deterministic():
    claimed = ['I10', 'E11.9']
    snapshot = copy.deepcopy(claimed)
    first = audit_baseline(PROSE, claimed)
    assert claimed == snapshot
    assert audit_baseline(PROSE, ['I10', 'E11.9']) == first


def test_input_validation():
    with pytest.raises(ValueError):
        audit_baseline(5, ['I10'])
    with pytest.raises(ValueError):
        audit_baseline(PROSE, 'I10')
    with pytest.raises(ValueError):
        audit_baseline(PROSE, ['I10', 5])


def test_baseline_perfect_on_goldset_closed_sentences():
    cases = build_gold_cases(14)
    run = run_eval(cases, audit_baseline, error_types=('missed_code', 'unsupported_code', 'negated_condition'))
    for etype in ('missed_code', 'unsupported_code', 'negated_condition'):
        tally = run['tally'][etype]
        assert tally['applicable'] > 0
        assert tally['detected'] == tally['applicable']
        assert tally['false_flags'] == 0
