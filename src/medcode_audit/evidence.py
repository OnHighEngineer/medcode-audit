"""Evidence-span verification. See docs/specs/010-evidence-verification.md.

Owns the verbatim evidence rule (one implementation, used by the spec-007
validator), reports span offsets for later report work, and flags SUPPORTED
verdicts that carry no quote as `unverified` instead of failing - frozen
history runs stub auditors without quotes. All outputs stay provisional.
"""
from __future__ import annotations

VERIFICATION_STATUSES = ('verified', 'unverified', 'invalid', 'not_applicable')


def find_span(note_text, quote):
    if not isinstance(note_text, str):
        raise ValueError('note_text must be a string')
    if not isinstance(quote, str) or not quote:
        raise ValueError('quote must be a nonempty string')
    index = note_text.find(quote)
    if index < 0:
        return None
    return (index, index + len(quote))


def verify_verdict(verdict, note_text) -> dict:
    # Lazy import: auditor_schema imports find_span from this module, so a
    # top-level import here would be circular.
    from .auditor_schema import VERDICTS
    if (not isinstance(verdict, dict)
            or not isinstance(verdict.get('code'), str)
            or verdict.get('verdict') not in VERDICTS):
        raise ValueError('verdict must be a dict with a code and a known verdict')
    if not isinstance(note_text, str):
        raise ValueError('note_text must be a string')
    quote = verdict.get('evidence_quote')
    record = {'code': verdict['code'], 'verdict': verdict['verdict'],
              'status': None, 'span': None}
    if quote is not None:
        if not isinstance(quote, str) or not quote:
            raise ValueError('evidence_quote must be a nonempty string')
        span = find_span(note_text, quote)
        if span is None:
            record['status'] = 'invalid'
        else:
            record['status'] = 'verified'
            record['span'] = span
    elif verdict['verdict'] == 'SUPPORTED':
        record['status'] = 'unverified'
    else:
        record['status'] = 'not_applicable'
    return record


def verify_evidence(verdicts, note_text) -> list:
    if not isinstance(verdicts, list):
        raise ValueError('verdicts must be a list')
    return [verify_verdict(v, note_text) for v in verdicts]


def verification_summary(records) -> dict:
    if not isinstance(records, list):
        raise ValueError('records must be a list')
    summary = {'total': len(records)}
    for status in VERIFICATION_STATUSES:
        summary[status] = sum(1 for r in records if r.get('status') == status)
    return summary
