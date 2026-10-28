"""Rule-based baseline auditor. See docs/specs/008-rule-baseline.md.

Closed lexical rules over the five provisional condition mappings, consulting
the spec-011 assertion detector. No NLP: high detection on closed-sentence
cases is expected (the same templates built the data), not evidence of
generalization. All counts stay provisional until the milestone 6 review.
"""
from __future__ import annotations

from .assertions import detect_assertions
from .missed import find_missed


def audit_baseline(note_text, claimed_codes) -> dict:
    if not isinstance(note_text, str):
        raise ValueError('note_text must be a string')
    if (not isinstance(claimed_codes, list)
            or any(not isinstance(c, str) for c in claimed_codes)):
        raise ValueError('claimed_codes must be a list of strings')
    states = {rec['code']: (rec['status'], rec['quote'])
              for rec in detect_assertions(note_text)}
    verdicts = []
    for code in claimed_codes:
        status, quote = states.get(code, ('absent', None))
        if status in ('affirmed', 'mentioned'):
            verdicts.append({'code': code, 'verdict': 'SUPPORTED',
                             'evidence_quote': quote})
        elif status == 'negated':
            verdicts.append({'code': code, 'verdict': 'UNSUPPORTED',
                             'evidence_quote': quote})
        else:
            verdicts.append({'code': code, 'verdict': 'UNSUPPORTED'})
    missed = [f['code'] for f in find_missed(note_text, claimed_codes)]
    return {'verdicts': verdicts, 'missed_codes': missed}
