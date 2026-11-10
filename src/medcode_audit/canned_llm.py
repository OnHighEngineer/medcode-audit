"""Gold-truth canned transport for the LLM auditor. See docs/specs/024-llm-regression-lane.md.

A deterministic offline transport that answers spec-009 prompts from the
committed cases' gold truth, so the LLM auditor's end-to-end wiring
(prompt build, reply parse, spec-007 validation, runner integration) is
guarded by the regression suite without any provider call. Replies mirror
committed note content only - no invented mappings. Fail-closed: unknown
notes and malformed prompts raise.
"""
from __future__ import annotations

import json

_NOTE_OPEN = 'NOTE:\n"""\n'
_NOTE_CLOSE = '\n"""\n'
_CLAIMED = 'CLAIMED_CODES_JSON:\n'


def _extract(prompt):
    if not isinstance(prompt, str):
        raise ValueError('prompt must be a string')
    start = prompt.find(_NOTE_OPEN)
    end = prompt.rfind(_NOTE_CLOSE)
    if start < 0 or end <= start:
        raise ValueError('prompt has no note fences')
    note = prompt[start + len(_NOTE_OPEN):end]
    tail = prompt[end + len(_NOTE_CLOSE):]
    if not tail.startswith(_CLAIMED):
        raise ValueError('prompt has no claimed-codes section')
    line = tail[len(_CLAIMED):].split('\n', 1)[0]
    try:
        claimed = json.loads(line)
    except json.JSONDecodeError as exc:
        raise ValueError(f'claimed codes not valid JSON: {exc}') from exc
    if not isinstance(claimed, list) or any(not isinstance(c, str) for c in claimed):
        raise ValueError('claimed codes must be a list of strings')
    return note, claimed


def make_gold_transport(cases):
    if not isinstance(cases, list) or any(not isinstance(c, dict) for c in cases):
        raise ValueError('cases must be a list of dicts')
    gold_by_note = {}
    for case in cases:
        note = case.get('note_text')
        if not isinstance(note, str) or not note:
            raise ValueError('each case needs a nonempty note_text')
        gold = {g['code']: g['evidence_quote'] for g in case.get('gold_codes', [])}
        if note in gold_by_note:
            if gold_by_note[note] != gold:
                raise ValueError('duplicate note_text with different gold codes')
            continue
        gold_by_note[note] = gold

    def transport(prompt):
        note, claimed = _extract(prompt)
        if note not in gold_by_note:
            raise ValueError('prompt note matches no case')
        gold = gold_by_note[note]
        verdicts = [
            {'code': code, 'verdict': 'SUPPORTED', 'evidence_quote': gold[code]}
            if code in gold else {'code': code, 'verdict': 'UNSUPPORTED'}
            for code in claimed
        ]
        missed = sorted(code for code in gold if code not in claimed)
        return json.dumps({'verdicts': verdicts, 'missed_codes': missed})

    return transport
