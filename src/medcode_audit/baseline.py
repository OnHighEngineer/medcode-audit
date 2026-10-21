"""Rule-based baseline auditor. See docs/specs/008-rule-baseline.md.

Closed lexical rules over the five provisional condition mappings and the
spec-003 assertion sentences. No NLP: high detection on closed-sentence cases
is expected (the same templates built the data), not evidence of
generalization. All counts stay provisional until the milestone 6 review.
"""
from __future__ import annotations

# (code, condition phrase, stem). Same five provisional mappings, intentionally
# isolated like the goldset's copy (see the day-9 decision entry).
_TABLE = (
    ('E11.9', 'type 2 diabetes without complications', 'diabet'),
    ('I10', 'essential hypertension', 'hypertens'),
    ('J45.30', 'mild persistent asthma, uncomplicated', 'asthma'),
    ('N18.31', 'chronic kidney disease stage 3a', 'kidney'),
    ('D50.9', 'iron deficiency anemia, unspecified', 'anemi'),
)
_AFFIRMED = 'Confirmed diagnosis: '
_NEGATED = 'Condition explicitly absent: '
_UNCERTAIN = 'Possible diagnosis, not confirmed: '


def _state(note, phrase, stem):
    affirmed = f'{_AFFIRMED}{phrase}.'
    if affirmed in note:
        return 'affirmed', affirmed
    negated = f'{_NEGATED}{phrase}.'
    if negated in note:
        return 'negated', negated
    if f'{_UNCERTAIN}{phrase}.' in note:
        return 'uncertain', None
    lowered = note.lower()
    for needle in (phrase, stem):
        index = lowered.find(needle)
        if index >= 0:
            return 'mentioned', note[index:index + len(needle)]
    return 'absent', None


def audit_baseline(note_text, claimed_codes) -> dict:
    if not isinstance(note_text, str):
        raise ValueError('note_text must be a string')
    if (not isinstance(claimed_codes, list)
            or any(not isinstance(c, str) for c in claimed_codes)):
        raise ValueError('claimed_codes must be a list of strings')
    states = {code: _state(note_text, phrase, stem)
              for code, phrase, stem in _TABLE}
    verdicts = []
    for code in claimed_codes:
        state, quote = states.get(code, ('absent', None))
        if state in ('affirmed', 'mentioned'):
            verdicts.append({'code': code, 'verdict': 'SUPPORTED',
                             'evidence_quote': quote})
        elif state == 'negated':
            verdicts.append({'code': code, 'verdict': 'UNSUPPORTED',
                             'evidence_quote': quote})
        else:
            verdicts.append({'code': code, 'verdict': 'UNSUPPORTED'})
    missed = [code for code, _, _ in _TABLE
              if states[code][0] in ('affirmed', 'mentioned')
              and code not in claimed_codes]
    return {'verdicts': verdicts, 'missed_codes': missed}
