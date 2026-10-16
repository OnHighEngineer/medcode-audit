"""Deterministic error injector. See docs/specs/004-error-injector.md.

Builds a claimed-code list from an immutable case. Gold truth is never edited.
"""
from __future__ import annotations

from .schema import ERROR_TYPES

# (code, condition phrase, stem). Same five provisional mappings as day 2/3.
_TABLE = (
    ('E11.9', 'type 2 diabetes without complications', 'diabet'),
    ('I10', 'essential hypertension', 'hypertens'),
    ('J45.30', 'mild persistent asthma, uncomplicated', 'asthma'),
    ('N18.31', 'chronic kidney disease stage 3a', 'kidney'),
    ('D50.9', 'iron deficiency anemia, unspecified', 'anemi'),
)
_NEGATED_PREFIX = 'Condition explicitly absent: '
_DEFERRED = ('upcoding', 'wrong_code')


def _result(case_id, error_type, seed, claimed=None, injection=None, finding=None,
            reason=None):
    ok = claimed is not None
    return {
        'source_case_id': case_id,
        'error_type': error_type,
        'seed': seed,
        'applicable': ok,
        'reason': None if ok else reason,
        'claimed_codes': claimed,
        'injection': injection,
        'expected_findings': [finding] if ok else [],
    }


def inject_error(case, error_type, seed=0) -> dict:
    """Return a claimed-code list with one known error, or an explicit inapplicable result."""
    if not isinstance(case, dict):
        raise ValueError('case must be a dict')
    if error_type not in ERROR_TYPES:
        raise ValueError(f'error_type must be one of {ERROR_TYPES}')
    if type(seed) is not int:
        raise ValueError('seed must be an int')
    case_id = case.get('id')
    note = case.get('note_text', '')
    gold = [g['code'] for g in case.get('gold_codes', [])]
    baseline = [{'code': c, 'origin': 'gold'} for c in gold]

    def fail(reason):
        return _result(case_id, error_type, seed, reason=reason)

    if error_type in _DEFERRED:
        return fail('deferred_unverified_mapping')
    if error_type == 'missed_code':
        if not gold:
            return fail('no_gold_code')
        target = gold[seed % len(gold)]
        claimed = [d for d in baseline if d['code'] != target]
        return _result(case_id, error_type, seed, claimed,
                       {'code': target, 'action': 'removed'},
                       {'code': target, 'finding': 'missed'})
    lowered = note.lower()
    if error_type == 'unsupported_code':
        cands = [c for c, phrase, stem in _TABLE
                 if c not in gold and phrase not in lowered and stem not in lowered]
        reason, finding = 'no_unmentioned_condition', 'unsupported'
    else:  # negated_condition
        cands = [c for c, phrase, _ in _TABLE
                 if c not in gold and f'{_NEGATED_PREFIX}{phrase}.' in note]
        reason, finding = 'no_negated_target', 'negated_claim'
    if not cands:
        return fail(reason)
    target = cands[seed % len(cands)]
    return _result(case_id, error_type, seed,
                   baseline + [{'code': target, 'origin': 'injected'}],
                   {'code': target, 'action': 'added'},
                   {'code': target, 'finding': finding})
