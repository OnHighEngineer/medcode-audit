"""Frozen tests for the spec-014 find_missed agent-loop tool."""
import pytest

from medcode_audit.agent_loop import run_agent_audit

NOTE = ('Confirmed diagnosis: type 2 diabetes without complications. '
        'Patient is recovering well.')
FINAL = ('{"final": {"verdicts": [{"code": "I10", "verdict": "UNSUPPORTED"}],'
         ' "missed_codes": ["E11.9"]}}')


def scripted(replies):
    queue = list(replies)
    calls = []

    def transport(prompt):
        calls.append(prompt)
        return queue.pop(0)
    transport.calls = calls
    return transport


def test_find_missed_tool_returns_evidence():
    replies = ['{"tool": "find_missed", "args": {"claimed_codes": ["I10"]}}',
               FINAL]
    transport = scripted(replies)
    result = run_agent_audit(NOTE, ['I10'], transport)
    assert result['missed_codes'] == ['E11.9']
    assert 'E11.9' in transport.calls[1]
    assert 'evidence_quote' in transport.calls[1]


def test_find_missed_tool_bad_args_raise():
    with pytest.raises(ValueError):
        run_agent_audit(NOTE, ['I10'],
                        scripted(['{"tool": "find_missed", "args": {}}']))
    with pytest.raises(ValueError):
        run_agent_audit(NOTE, ['I10'],
                        scripted(['{"tool": "find_missed", "args": '
                                  '{"claimed_codes": "I10"}}']))
