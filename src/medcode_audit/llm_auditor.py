"""LLM auditor v1, offline-first. See docs/specs/009-llm-auditor-v1.md.

The model call is an injected transport(prompt) -> reply_text, so the suite
runs on canned replies with no network and no credentials. Malformed replies
fail closed; a fabricated evidence quote is rejected by the spec-007
validation. All outputs stay provisional until the milestone 6 review.
"""
from __future__ import annotations

import json

from .auditor_schema import VERDICTS, validate_auditor_output

_INSTRUCTIONS = (
    'You audit claimed medical codes against one synthetic clinical note. '
    'For every claimed code return one verdict: SUPPORTED (the note supports '
    'the code; copy the verbatim supporting text into evidence_quote), '
    'UNSUPPORTED (no supporting text), WRONG_SPECIFICITY (right condition, '
    'wrong precision), or MISSED. List conditions the note supports but no '
    'claimed code covers under missed_codes. Answer with one JSON object only: '
    '{"verdicts": [{"code", "verdict", "evidence_quote"?}], "missed_codes": []}.'
)


def build_prompt(note_text, claimed_codes) -> str:
    if not isinstance(note_text, str):
        raise ValueError('note_text must be a string')
    if (not isinstance(claimed_codes, list)
            or any(not isinstance(c, str) for c in claimed_codes)):
        raise ValueError('claimed_codes must be a list of strings')
    return (f'{_INSTRUCTIONS}\nVerdicts: {", ".join(VERDICTS)}.\n'
            f'NOTE:\n"""\n{note_text}\n"""\n'
            f'CLAIMED_CODES_JSON:\n{json.dumps(claimed_codes)}\n'
            'Every SUPPORTED verdict needs a verbatim evidence_quote from the note.')


def parse_model_reply(reply_text) -> dict:
    if not isinstance(reply_text, str):
        raise ValueError('reply_text must be a string')
    start, end = reply_text.find('{'), reply_text.rfind('}')
    if start < 0 or end <= start:
        raise ValueError('no JSON object in model reply')
    try:
        parsed = json.loads(reply_text[start:end + 1])
    except json.JSONDecodeError as exc:
        raise ValueError(f'model reply is not valid JSON: {exc}') from exc
    if not isinstance(parsed, dict):
        raise ValueError('model reply must be a JSON object')
    return parsed


def static_transport(reply):
    def transport(prompt):
        return reply
    return transport


def make_llm_auditor(transport):
    if not callable(transport):
        raise ValueError('transport must be callable')

    def auditor(note_text, claimed_codes):
        prompt = build_prompt(note_text, claimed_codes)
        reply = parse_model_reply(transport(prompt))
        return validate_auditor_output(reply, list(claimed_codes),
                                       note_text=note_text)
    return auditor
