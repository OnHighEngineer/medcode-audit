"""Assertion-status detection. See docs/specs/011-assertion-detection.md.

One detector for affirmed / negated / uncertain / mentioned / absent /
conflict over the five provisional conditions. Closed spec-003 sentences
classify exactly; prose mentions are lexical and marked as such; contradictory
closed sentences surface as `conflict`, never a silent winner. No general
prose negation or paraphrase detection. All outputs stay provisional.
"""
from __future__ import annotations

from .evidence import find_span

ASSERTION_STATUSES = ('affirmed', 'negated', 'uncertain', 'mentioned',
                      'absent', 'conflict')

# (code, condition phrase, stem). Same five provisional mappings, intentionally
# isolated like the goldset's and baseline's copies.
_TABLE = (
    ('E11.9', 'type 2 diabetes without complications', 'diabet'),
    ('I10', 'essential hypertension', 'hypertens'),
    ('J45.30', 'mild persistent asthma, uncomplicated', 'asthma'),
    ('N18.31', 'chronic kidney disease stage 3a', 'kidney'),
    ('D50.9', 'iron deficiency anemia, unspecified', 'anemi'),
)
_CLOSED = (('affirmed', 'Confirmed diagnosis: '),
           ('negated', 'Condition explicitly absent: '),
           ('uncertain', 'Possible diagnosis, not confirmed: '))


def _detect_one(note, code, phrase, stem) -> dict:
    matches = []
    for status, prefix in _CLOSED:
        sentence = f'{prefix}{phrase}.'
        span = find_span(note, sentence)
        if span is not None:
            matches.append((status, sentence, span))
    record = {'code': code, 'status': None, 'quote': None, 'span': None}
    if len({m[0] for m in matches}) > 1:
        record['status'] = 'conflict'
        record['conflicting'] = [sentence for _, sentence, _ in matches]
    elif matches:
        status, sentence, span = matches[0]
        record.update(status=status, quote=sentence, span=span)
    else:
        lowered = note.lower()
        for needle in (phrase, stem):
            index = lowered.find(needle)
            if index >= 0:
                record.update(status='mentioned',
                              quote=note[index:index + len(needle)],
                              span=(index, index + len(needle)))
                break
        else:
            record['status'] = 'absent'
    return record


def detect_assertions(note_text) -> list:
    if not isinstance(note_text, str):
        raise ValueError('note_text must be a string')
    return [_detect_one(note_text, code, phrase, stem)
            for code, phrase, stem in _TABLE]


def status_for(note_text, code) -> dict:
    if not isinstance(note_text, str):
        raise ValueError('note_text must be a string')
    for entry in _TABLE:
        if entry[0] == code:
            return _detect_one(note_text, *entry)
    raise ValueError(f'unknown code: {code}')
