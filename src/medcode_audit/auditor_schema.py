"""Auditor output schema and validators. See docs/specs/007-auditor-output-schema.md.

One checked shape for every auditor (stub, rule baseline, LLM). Validation
fails closed; an optional evidence quote must be a verbatim note substring
whenever the caller supplies the note. All outputs stay provisional.
"""
from __future__ import annotations

VERDICTS = ('SUPPORTED', 'UNSUPPORTED', 'WRONG_SPECIFICITY', 'MISSED')


def validate_auditor_output(output, claimed_codes, note_text=None) -> dict:
    if not isinstance(output, dict):
        raise ValueError('auditor output must be a dict')
    verdicts, missed = output.get('verdicts'), output.get('missed_codes')
    if not isinstance(verdicts, list) or not isinstance(missed, list):
        raise ValueError('auditor output needs verdicts and missed_codes lists')
    if any(not isinstance(m, str) for m in missed):
        raise ValueError('missed_codes must be strings')
    if (not isinstance(claimed_codes, list)
            or any(not isinstance(c, str) for c in claimed_codes)):
        raise ValueError('claimed_codes must be a list of strings')
    normalized = []
    seen = set()
    for entry in verdicts:
        if (not isinstance(entry, dict)
                or not isinstance(entry.get('code'), str)
                or entry.get('verdict') not in VERDICTS):
            raise ValueError('each verdict needs a code and a known verdict')
        if entry['code'] in seen:
            raise ValueError('duplicate verdict for a code')
        seen.add(entry['code'])
        clean = {'code': entry['code'], 'verdict': entry['verdict']}
        if 'evidence_quote' in entry:
            quote = entry['evidence_quote']
            if not isinstance(quote, str) or not quote:
                raise ValueError('evidence_quote must be a nonempty string')
            if note_text is not None and quote not in note_text:
                raise ValueError('evidence_quote must be a verbatim note substring')
            clean['evidence_quote'] = quote
        normalized.append(clean)
    if sorted(seen) != sorted(claimed_codes):
        raise ValueError('verdicts must cover exactly the claimed codes')
    return {'verdicts': normalized, 'missed_codes': list(missed)}
