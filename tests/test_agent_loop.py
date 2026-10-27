"""Frozen tests for spec 013 (agent loop). Written before the module."""
import pytest

from medcode_audit.agent_loop import (MAX_STEPS, make_agent_auditor,
                                      run_agent_audit)

NOTE = ('Confirmed diagnosis: type 2 diabetes without complications. '
        'Patient is recovering well.')
FINAL = ('{"final": {"verdicts": [{"code": "E11.9", "verdict": "SUPPORTED", '
         '"evidence_quote": "Confirmed diagnosis: type 2 diabetes without '
         'complications."}], "missed_codes": []}}')


def scripted_transport(replies):
    queue = list(replies)
    calls = []

    def transport(prompt):
        calls.append(prompt)
        if not queue:
            raise AssertionError('transport called more times than scripted')
        return queue.pop(0)
    transport.calls = calls
    return transport


def test_single_turn_final_no_tools():
    transport = scripted_transport([FINAL])
    result = run_agent_audit(NOTE, ['E11.9'], transport)
    assert result['verdicts'][0]['verdict'] == 'SUPPORTED'
    assert result['missed_codes'] == []
    assert len(transport.calls) == 1


def test_multi_turn_with_lookup_and_quote_check():
    replies = [
        '{"tool": "lookup_code", "args": {"code": "E11.9"}}',
        '{"tool": "verify_quote", "args": {"code": "E11.9", "quote": '
        '"Confirmed diagnosis: type 2 diabetes without complications."}}',
        FINAL,
    ]
    transport = scripted_transport(replies)
    result = run_agent_audit(NOTE, ['E11.9'], transport)
    assert result['verdicts'][0]['code'] == 'E11.9'
    assert len(transport.calls) == 3
    # transcript grows: each later prompt carries earlier tool results
    assert 'Type 2 diabetes mellitus without complications' in transport.calls[1]
    assert 'verified' in transport.calls[2]


def test_detect_assertions_tool_returns_records():
    replies = ['{"tool": "detect_assertions", "args": {}}', FINAL]
    transport = scripted_transport(replies)
    run_agent_audit(NOTE, ['E11.9'], transport)
    assert 'E11.9' in transport.calls[1]
    assert 'affirmed' in transport.calls[1]


def test_unknown_code_is_an_observable_tool_error_not_a_crash():
    replies = [
        '{"tool": "lookup_code", "args": {"code": "A00.0"}}',
        '{"final": {"verdicts": [{"code": "A00.0", "verdict": "UNSUPPORTED"}],'
        ' "missed_codes": []}}',
    ]
    transport = scripted_transport(replies)
    result = run_agent_audit(NOTE, ['A00.0'], transport)
    assert result['verdicts'][0]['verdict'] == 'UNSUPPORTED'
    assert '"ok": false' in transport.calls[1]


def test_verify_quote_invalid_is_returned_not_raised():
    replies = [
        '{"tool": "verify_quote", "args": {"code": "E11.9", "quote": '
        '"text not in the note"}}',
        FINAL,
    ]
    transport = scripted_transport(replies)
    run_agent_audit(NOTE, ['E11.9'], transport)
    assert 'invalid' in transport.calls[1]


@pytest.mark.parametrize('reply', ['not json at all', '[1, 2]',
                                   '{"answer": 42}', '{"tool": "hack"}',
                                   '{"tool": "lookup_code"}',
                                   '{"tool": "lookup_code", "args": "E11.9"}',
                                   '{"tool": "lookup_code", "args": {"code": 9}}',
                                   '{"tool": "detect_assertions", "args": {"x": 1}}'])
def test_protocol_violations_raise_value_error(reply):
    transport = scripted_transport([reply, FINAL])
    with pytest.raises(ValueError):
        run_agent_audit(NOTE, ['E11.9'], transport)


def test_max_steps_exceeded_raises_runtime_error():
    transport = scripted_transport(
        ['{"tool": "detect_assertions", "args": {}}'] * (MAX_STEPS + 1))
    with pytest.raises(RuntimeError):
        run_agent_audit(NOTE, ['E11.9'], transport)


def test_final_is_spec007_validated_fabricated_quote_raises():
    bad = ('{"final": {"verdicts": [{"code": "E11.9", "verdict": "SUPPORTED", '
           '"evidence_quote": "not in the note at all"}], "missed_codes": []}}')
    with pytest.raises(ValueError):
        run_agent_audit(NOTE, ['E11.9'], scripted_transport([bad]))


def test_final_missing_claimed_code_raises():
    bad = '{"final": {"verdicts": [], "missed_codes": []}}'
    with pytest.raises(ValueError):
        run_agent_audit(NOTE, ['E11.9'], scripted_transport([bad]))


def test_transport_exception_propagates():
    def boom(prompt):
        raise ConnectionError('offline')
    with pytest.raises(ConnectionError):
        run_agent_audit(NOTE, ['E11.9'], boom)


@pytest.mark.parametrize('note, codes', [(None, ['E11.9']), (NOTE, 'E11.9'),
                                         (NOTE, ['E11.9', 9]), (9, ['E11.9'])])
def test_input_type_checks(note, codes):
    with pytest.raises(ValueError):
        run_agent_audit(note, codes, scripted_transport([FINAL]))


def test_make_agent_auditor_is_runner_compatible():
    auditor = make_agent_auditor(scripted_transport([FINAL]))
    result = auditor(NOTE, ['E11.9'])
    assert result['verdicts'][0]['code'] == 'E11.9'


def test_max_steps_validation():
    with pytest.raises(ValueError):
        run_agent_audit(NOTE, ['E11.9'], scripted_transport([FINAL]),
                        max_steps=0)
    with pytest.raises(ValueError):
        make_agent_auditor(scripted_transport([FINAL]), max_steps='8')
