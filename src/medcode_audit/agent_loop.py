"""Agent loop with tools, offline-first. See docs/specs/013-agent-loop.md.

The model speaks a one-JSON-object-per-turn protocol over a spec-009 style
injected transport; between turns it may call three deterministic local
tools (spec-012 code lookup, spec-010 quote verification, spec-011 assertion
detection). Protocol violations raise, tool errors are observable results,
and the final answer passes spec-007 validation with the note. No network,
no credentials, no partial scores.
"""
from __future__ import annotations

import json

from .assertions import detect_assertions
from .auditor_schema import validate_auditor_output
from .code_lookup import lookup
from .evidence import find_span
from .llm_auditor import parse_model_reply
from .missed import find_missed

MAX_STEPS = 8

_INSTRUCTIONS = (
    'You audit claimed medical codes against one synthetic clinical note, '
    'one step per turn. Each turn answer with ONE JSON object: either '
    '{"tool": "lookup_code", "args": {"code": "..."}} to read a code\'s '
    'official description and family, {"tool": "verify_quote", "args": '
    '{"code": "...", "quote": "..."}} to check text is verbatim in the note, '
    '{"tool": "detect_assertions", "args": {}} to list detected conditions, '
    '{"tool": "find_missed", "args": {"claimed_codes": [...]}} to list '
    'supported conditions no claim covers, with evidence, '
    'or {"final": {"verdicts": [...], "missed_codes": [...]}} when done. '
    'Every SUPPORTED verdict needs a verbatim evidence_quote from the note.')


def _check_inputs(note_text, claimed_codes):
    if not isinstance(note_text, str):
        raise ValueError('note_text must be a string')
    if (not isinstance(claimed_codes, list)
            or any(not isinstance(c, str) for c in claimed_codes)):
        raise ValueError('claimed_codes must be a list of strings')


def _initial_prompt(note_text, claimed_codes):
    return (f'{_INSTRUCTIONS}\nNOTE:\n"""\n{note_text}\n"""\n'
            f'CLAIMED_CODES_JSON:\n{json.dumps(claimed_codes)}')


def _run_tool(note_text, name, args):
    if name == 'lookup_code':
        code = args.get('code')
        if not isinstance(code, str):
            raise ValueError('lookup_code args.code must be a string')
        try:
            return {'ok': True, 'result': lookup(code)}
        except (ValueError, LookupError) as exc:
            return {'ok': False, 'error': str(exc)}
    if name == 'verify_quote':
        code, quote = args.get('code'), args.get('quote')
        if not isinstance(code, str) or not isinstance(quote, str) or not quote:
            raise ValueError('verify_quote needs string code and nonempty quote')
        span = find_span(note_text, quote)
        if span is None:
            return {'ok': True, 'result': {'status': 'invalid', 'span': None}}
        return {'ok': True, 'result': {'status': 'verified', 'span': list(span)}}
    if name == 'find_missed':
        codes = args.get('claimed_codes')
        if (not isinstance(codes, list)
                or any(not isinstance(c, str) for c in codes)):
            raise ValueError('find_missed args.claimed_codes must be a list of strings')
        result = [dict(f, span=list(f['span'])) if f['span'] else f
                  for f in find_missed(note_text, codes)]
        return {'ok': True, 'result': result}
    if name == 'detect_assertions':
        if args:
            raise ValueError('detect_assertions takes no args')
        return {'ok': True, 'result': detect_assertions(note_text)}
    raise ValueError(f'unknown tool: {name!r}')


def run_agent_audit(note_text, claimed_codes, transport, max_steps=MAX_STEPS):
    _check_inputs(note_text, claimed_codes)
    if not callable(transport):
        raise ValueError('transport must be callable')
    if not isinstance(max_steps, int) or isinstance(max_steps, bool) or max_steps < 1:
        raise ValueError('max_steps must be a positive integer')

    transcript = _initial_prompt(note_text, claimed_codes)
    for _ in range(max_steps):
        reply = parse_model_reply(transport(transcript))
        if 'final' in reply:
            return validate_auditor_output(reply['final'],
                                           list(claimed_codes),
                                           note_text=note_text)
        if 'tool' not in reply or not isinstance(reply.get('args'), dict):
            raise ValueError('reply must be a tool call or a final answer')
        result = _run_tool(note_text, reply['tool'], reply['args'])
        transcript += (f'\nASSISTANT:\n{json.dumps(reply)}'
                       f'\nTOOL_RESULT:\n{json.dumps(result)}')
    raise RuntimeError(f'no final answer within {max_steps} tool steps')


def make_agent_auditor(transport, max_steps=MAX_STEPS):
    if not isinstance(max_steps, int) or isinstance(max_steps, bool) or max_steps < 1:
        raise ValueError('max_steps must be a positive integer')

    def auditor(note_text, claimed_codes):
        return run_agent_audit(note_text, claimed_codes, transport,
                               max_steps=max_steps)
    return auditor
