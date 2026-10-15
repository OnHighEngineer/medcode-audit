"""Closed synthetic assertion scenarios, not a clinical NLP or coding policy."""
from __future__ import annotations

# Intentionally isolated from the day-2 generator's private template constants.
_CONDITIONS = (
    ('E11.9', 'type 2 diabetes without complications'),
    ('I10', 'essential hypertension'),
    ('J45.30', 'mild persistent asthma, uncomplicated'),
    ('N18.31', 'chronic kidney disease stage 3a'),
    ('D50.9', 'iron deficiency anemia, unspecified'),
)
_PREFIXES = {
    'affirmed': 'Confirmed diagnosis: ',
    'negated': 'Condition explicitly absent: ',
    'uncertain': 'Possible diagnosis, not confirmed: ',
}


def make_assertion_case(case_id, assertions) -> dict:
    """Build a case from explicit states; never infer gold labels from text."""
    if not isinstance(case_id, str) or not case_id.strip():
        raise ValueError('case_id must be a nonempty string')
    if not isinstance(assertions, list) or not assertions:
        raise ValueError('assertions must be a nonempty list of code/status pairs')
    conditions = dict(_CONDITIONS)
    seen, sentences, gold = set(), [], []
    for item in assertions:
        if not isinstance(item, (tuple, list)) or len(item) != 2:
            raise ValueError('assertions must contain code/status pairs')
        code, status = item
        if (not isinstance(code, str) or code not in conditions
                or not isinstance(status, str) or status not in _PREFIXES):
            raise ValueError('assertions contain an unknown code or status')
        if code in seen:
            raise ValueError('assertions contain a duplicate condition')
        seen.add(code)
        sentence = _PREFIXES[status] + conditions[code] + '.'
        sentences.append(sentence)
        if status == 'affirmed':
            gold.append({'code': code, 'evidence_quote': sentence})
    return {
        'id': case_id,
        'synthetic': True,
        'note_text': 'SYNTHETIC NOTE. Assertion exercise. ' + ' '.join(sentences),
        'gold_codes': gold,
        'injected_errors': [],
    }


def build_gold_cases(start_id=14) -> list[dict]:
    """Return the fixed 37-scenario day-3 batch without file or RNG effects."""
    if type(start_id) is not int or start_id < 1:
        raise ValueError('start_id must be a positive integer')
    codes = [code for code, _ in _CONDITIONS]
    scenarios = []
    for status in ('affirmed', 'negated', 'uncertain'):
        scenarios.extend([[(code, status)] for code in codes])
    for offset in (1, 2):
        scenarios.extend([
            [(code, 'affirmed'), (codes[(i + offset) % 5], 'negated')]
            for i, code in enumerate(codes)
        ])
    for other_status in ('uncertain', 'affirmed'):
        scenarios.extend([
            [(code, 'affirmed'), (codes[(i + 1) % 5], other_status)]
            for i, code in enumerate(codes)
        ])
    for status in ('negated', 'uncertain'):
        scenarios.append([(code, status) for code in codes])
    return [make_assertion_case(f'gen-{start_id + i:03d}', scenario)
            for i, scenario in enumerate(scenarios)]
