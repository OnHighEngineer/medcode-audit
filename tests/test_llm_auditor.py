import copy
import json

import pytest

from medcode_audit.auditor_schema import validate_auditor_output
from medcode_audit.goldset import build_gold_cases
from medcode_audit.llm_auditor import (build_prompt, make_llm_auditor,
                                       parse_model_reply, static_transport)
from medcode_audit.runner import run_eval

NOTE = 'SYNTHETIC NOTE. Assertion exercise. Confirmed diagnosis: essential hypertension.'

GOOD_REPLY = json.dumps({
    'verdicts': [{'code': 'I10', 'verdict': 'SUPPORTED',
                  'evidence_quote': 'Confirmed diagnosis: essential hypertension.'},
                 {'code': 'E11.9', 'verdict': 'UNSUPPORTED'}],
    'missed_codes': []})


def test_prompt_contains_note_codes_verdicts_and_quote_requirement():
    prompt = build_prompt(NOTE, ['I10', 'E11.9'])
    assert NOTE in prompt
    assert 'I10' in prompt and 'E11.9' in prompt
    for name in ('SUPPORTED', 'UNSUPPORTED', 'WRONG_SPECIFICITY', 'MISSED'):
        assert name in prompt
    assert 'evidence_quote' in prompt and 'verbatim' in prompt
    assert 'missed_codes' in prompt


def test_build_prompt_validates_inputs():
    with pytest.raises(ValueError):
        build_prompt(5, ['I10'])
    with pytest.raises(ValueError):
        build_prompt(NOTE, 'I10')
    with pytest.raises(ValueError):
        build_prompt(NOTE, ['I10', 5])


def test_parse_clean_json_and_fenced_json():
    assert parse_model_reply(GOOD_REPLY)['missed_codes'] == []
    fenced = 'Here is the audit:\n```json\n' + GOOD_REPLY + '\n```\nDone.'
    assert parse_model_reply(fenced)['verdicts'][0]['code'] == 'I10'


def test_parse_rejects_unparseable_replies():
    for bad in ('no json here', '{broken', json.dumps([1, 2]), '', 5, None):
        with pytest.raises(ValueError):
            parse_model_reply(bad)


def test_auditor_output_satisfies_spec_007():
    auditor = make_llm_auditor(static_transport(GOOD_REPLY))
    result = auditor(NOTE, ['I10', 'E11.9'])
    assert validate_auditor_output(result, ['I10', 'E11.9'], note_text=NOTE) == result


def test_fabricated_quote_fails_closed():
    reply = json.dumps({'verdicts': [{'code': 'I10', 'verdict': 'SUPPORTED',
                                      'evidence_quote': 'not in the note'}],
                        'missed_codes': []})
    auditor = make_llm_auditor(static_transport(reply))
    with pytest.raises(ValueError):
        auditor(NOTE, ['I10'])


def test_malformed_reply_fails_closed():
    auditor = make_llm_auditor(static_transport('the model refused'))
    with pytest.raises(ValueError):
        auditor(NOTE, ['I10'])


def test_shape_violations_fail_closed():
    missing_claim = json.dumps({'verdicts': [{'code': 'I10', 'verdict': 'SUPPORTED'}],
                                'missed_codes': []})
    auditor = make_llm_auditor(static_transport(missing_claim))
    with pytest.raises(ValueError):
        auditor(NOTE, ['I10', 'E11.9'])


def test_transport_receives_built_prompt_and_exceptions_propagate():
    seen = []

    def recorder(prompt):
        seen.append(prompt)
        return GOOD_REPLY

    make_llm_auditor(recorder)(NOTE, ['I10', 'E11.9'])
    assert seen == [build_prompt(NOTE, ['I10', 'E11.9'])]

    def boom(prompt):
        raise RuntimeError('provider down')

    with pytest.raises(RuntimeError):
        make_llm_auditor(boom)(NOTE, ['I10', 'E11.9'])


def test_transport_must_be_callable():
    with pytest.raises(ValueError):
        make_llm_auditor('not callable')


def test_inputs_not_mutated_and_deterministic():
    claimed = ['I10', 'E11.9']
    snapshot = copy.deepcopy(claimed)
    auditor = make_llm_auditor(static_transport(GOOD_REPLY))
    first = auditor(NOTE, claimed)
    assert claimed == snapshot
    assert auditor(NOTE, ['I10', 'E11.9']) == first


def test_canned_perfect_auditor_runs_full_eval_offline():
    cases = build_gold_cases(14)
    by_note = {c['note_text']: c for c in cases}

    def canned_model(prompt):
        note = prompt.split('NOTE:\n"""\n', 1)[1].split('\n"""', 1)[0]
        claimed = json.loads(prompt.split('CLAIMED_CODES_JSON:\n', 1)[1].split('\n', 1)[0])
        gold = {g['code']: g['evidence_quote'] for g in by_note[note]['gold_codes']}
        verdicts = [{'code': c, 'verdict': 'SUPPORTED', 'evidence_quote': gold[c]}
                    if c in gold else {'code': c, 'verdict': 'UNSUPPORTED'}
                    for c in claimed]
        return json.dumps({'verdicts': verdicts,
                           'missed_codes': sorted(set(gold) - set(claimed))})

    auditor = make_llm_auditor(canned_model)
    run = run_eval(cases, auditor,
                   error_types=('missed_code', 'unsupported_code', 'negated_condition'))
    for etype in ('missed_code', 'unsupported_code', 'negated_condition'):
        tally = run['tally'][etype]
        assert tally['detected'] == tally['applicable'] > 0
        assert tally['false_flags'] == 0
