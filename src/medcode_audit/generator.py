"""Seeded, identifier-free synthetic notes. See spec 002; labels are provisional."""
from __future__ import annotations

import random

_CONDITIONS = (
    ('E11.9', 'type 2 diabetes without complications'),
    ('I10', 'essential hypertension'),
    ('J45.30', 'mild persistent asthma, uncomplicated'),
    ('N18.31', 'chronic kidney disease stage 3a'),
    ('D50.9', 'iron deficiency anemia, unspecified'),
)
_WRAPPERS = (
    ('SYNTHETIC NOTE. Assessment: ', '. Routine follow-up.'),
    ('SYNTHETIC NOTE. Documented diagnosis: ', '. Review visit.'),
    ('SYNTHETIC NOTE. Active condition: ', '. Follow-up assessment.'),
)


def generate_cases(count=10, seed=0, start_id=4) -> list[dict]:
    """Return independent JSON-ready cases; never read or write patient data.

    Five consecutive cases cover all five conditions. Seed changes wording only.
    The caller must choose a fresh ID range when combining generated batches.
    """
    for name, value, minimum in (
        ('count', count, 0), ('seed', seed, None), ('start_id', start_id, 1)
    ):
        if type(value) is not int or (minimum is not None and value < minimum):
            raise ValueError(f'{name} must be an integer' + (
                f' >= {minimum}' if minimum is not None else ''
            ))
    rng = random.Random(seed)
    cases = []
    for index in range(count):
        code, quote = _CONDITIONS[index % len(_CONDITIONS)]
        prefix, suffix = rng.choice(_WRAPPERS)
        cases.append({
            'id': f'gen-{start_id + index:03d}',
            'synthetic': True,
            'note_text': prefix + quote + suffix,
            'gold_codes': [{'code': code, 'evidence_quote': quote}],
            'injected_errors': [],
        })
    return cases
