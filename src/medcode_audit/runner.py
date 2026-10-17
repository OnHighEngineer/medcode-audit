"""Eval runner skeleton. See docs/specs/005-eval-runner.md.

Applies the injector to cases, feeds claims to a pluggable auditor and counts
whether each expected finding was caught. Counts are provisional.
"""
from __future__ import annotations

from .injector import inject_error
from .schema import ERROR_TYPES

VERDICTS = ('SUPPORTED', 'UNSUPPORTED', 'WRONG_SPECIFICITY', 'MISSED')
_DEFERRED_REASON = 'deferred_unverified_mapping'


def _check_output(out, claimed):
    if not isinstance(out, dict):
        raise ValueError('auditor output must be a dict')
    verdicts, missed = out.get('verdicts'), out.get('missed_codes')
    if not isinstance(verdicts, list) or not isinstance(missed, list):
        raise ValueError('auditor output needs verdicts and missed_codes lists')
    if any(not isinstance(m, str) for m in missed):
        raise ValueError('missed_codes must be strings')
    by_code = {}
    for v in verdicts:
        if (not isinstance(v, dict) or not isinstance(v.get('code'), str)
                or v.get('verdict') not in VERDICTS):
            raise ValueError('each verdict needs a code and a known verdict')
        if v['code'] in by_code:
            raise ValueError('duplicate verdict for a code')
        by_code[v['code']] = v['verdict']
    if sorted(by_code) != sorted(claimed):
        raise ValueError('verdicts must cover exactly the claimed codes')
    return by_code, missed


def _caught(finding, by_code, missed):
    if finding['finding'] == 'missed':
        return finding['code'] in missed
    return by_code.get(finding['code']) == 'UNSUPPORTED'


def run_eval(cases, auditor, error_types=ERROR_TYPES, seed=0) -> dict:
    if not isinstance(cases, list):
        raise ValueError('cases must be a list')
    if not callable(auditor):
        raise ValueError('auditor must be callable')
    types = list(error_types)
    if any(t not in ERROR_TYPES for t in types):
        raise ValueError(f'error_types must be from {ERROR_TYPES}')
    if type(seed) is not int:
        raise ValueError('seed must be an int')
    tally = {t: {'applicable': 0, 'detected': 0, 'not_detected': 0,
                 'inapplicable': 0, 'false_flags': 0, 'reasons': {}} for t in types}
    results = []
    for case in cases:
        for etype in types:
            inj = inject_error(case, etype, seed)
            row = tally[etype]
            rec = {'source_case_id': inj['source_case_id'], 'error_type': etype,
                   'seed': seed, 'status': 'inapplicable', 'reason': inj['reason'],
                   'expected_findings': inj['expected_findings'], 'false_flags': []}
            if not inj['applicable']:
                row['inapplicable'] += 1
                row['reasons'][inj['reason']] = row['reasons'].get(inj['reason'], 0) + 1
                results.append(rec)
                continue
            claimed = [c['code'] for c in inj['claimed_codes']]
            out = auditor(str(case.get('note_text', '')), list(claimed))
            by_code, missed = _check_output(out, claimed)
            ok = all(_caught(f, by_code, missed) for f in inj['expected_findings'])
            rec['status'] = 'detected' if ok else 'not_detected'
            rec['false_flags'] = [c['code'] for c in inj['claimed_codes']
                                  if c['origin'] == 'gold'
                                  and by_code[c['code']] != 'SUPPORTED']
            row['applicable'] += 1
            row['detected' if ok else 'not_detected'] += 1
            row['false_flags'] += len(rec['false_flags'])
            results.append(rec)
    return {'provisional': True, 'seed': seed, 'results': results, 'tally': tally}


def format_report(run) -> str:
    lines = ['PROVISIONAL: synthetic labels, no clinical review yet (milestone 6). '
             'Counts only, not trusted scores.', f"seed {run['seed']}"]
    for etype, t in run['tally'].items():
        total = t['applicable'] + t['inapplicable']
        if total and t['reasons'].get(_DEFERRED_REASON) == total:
            lines.append(f'{etype}: not implemented ({_DEFERRED_REASON}), '
                         f'{total} cases skipped')
            continue
        lines.append(f"{etype}: detected {t['detected']}/{t['applicable']}, "
                     f"not detected {t['not_detected']}, "
                     f"inapplicable {t['inapplicable']}, "
                     f"false flags on gold claims {t['false_flags']}")
    return '\n'.join(lines) + '\n'
