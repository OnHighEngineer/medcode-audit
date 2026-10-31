"""Failure analysis report. See docs/specs/017-failure-analysis.md.

Breaks a run result's not_detected rows and false flags down by error
type and case stratum (spec-006 marker stratum plus a gold-count band)
so a weak auditor's failures are explainable instead of a single count.
Deterministic, provisional, no percentages. Reporting only.
"""
from __future__ import annotations

from .assertions import detect_assertions
from .review import stratum_key
from .upcoding import assess_upcoding

BANDS = ('no_gold', 'single_condition', 'multi_condition')

_HEADER = ('FAILURE ANALYSIS (PROVISIONAL): synthetic labels, no clinical '
           'review yet (milestone 6). Explains where failures concentrate; '
           'counts only, not trusted scores.')


def condition_band(case) -> str:
    if not isinstance(case, dict) or not isinstance(case.get('gold_codes'), list):
        raise ValueError('case must be a dict with a list gold_codes')
    n = len(case['gold_codes'])
    return BANDS[0] if n == 0 else BANDS[1] if n == 1 else BANDS[2]


def _index_cases(cases):
    if not isinstance(cases, list):
        raise ValueError('cases must be a list')
    index = {}
    for c in cases:
        if not isinstance(c, dict) or not isinstance(c.get('id'), str) or not c['id']:
            raise ValueError('each case needs a nonempty string id')
        stratum_key(c)  # reuses the spec-006 note_text validation
        if c['id'] in index:
            raise ValueError(f"duplicate case id: {c['id']}")
        index[c['id']] = c
    return index


def _empty_breakdown():
    return {'total': 0, 'by_stratum': {}, 'by_band': {}, 'cases': []}


def analyze_run(run, cases) -> dict:
    if not isinstance(run, dict) or not isinstance(run.get('results'), list):
        raise ValueError('run must be a dict with a list results')
    index = _index_cases(cases)
    types = list(run.get('tally', {}))
    if not types:
        seen = []
        for rec in run['results']:
            if isinstance(rec, dict) and rec.get('error_type') not in seen:
                seen.append(rec.get('error_type'))
        types = seen
    not_detected = {t: _empty_breakdown() for t in types}
    false_flags = {t: _empty_breakdown() for t in types}
    inapplicable = {t: {} for t in types}
    for rec in run['results']:
        if not isinstance(rec, dict):
            raise ValueError('each run result must be a dict')
        cid, etype = rec.get('source_case_id'), rec.get('error_type')
        if cid not in index:
            raise ValueError(f'result names an unknown case: {cid}')
        if etype not in not_detected:
            raise ValueError(f'result names an error type outside the tally: {etype}')
        source = index[cid]
        stratum, band = stratum_key(source), condition_band(source)
        status = rec.get('status')
        if status == 'not_detected':
            b = not_detected[etype]
            b['total'] += 1
            b['by_stratum'][stratum] = b['by_stratum'].get(stratum, 0) + 1
            b['by_band'][band] = b['by_band'].get(band, 0) + 1
            b['cases'].append(cid)
        elif status == 'inapplicable':
            reason = rec.get('reason')
            inapplicable[etype][reason] = inapplicable[etype].get(reason, 0) + 1
        flags = rec.get('false_flags') or []
        if flags:
            f = false_flags[etype]
            f['total'] += len(flags)
            f['by_stratum'][stratum] = f['by_stratum'].get(stratum, 0) + 1
            f['by_band'][band] = f['by_band'].get(band, 0) + 1
            f['cases'].append({'case_id': cid, 'codes': sorted(flags)})
    for b in not_detected.values():
        b['cases'] = sorted(b['cases'])
    for f in false_flags.values():
        f['cases'] = sorted(f['cases'], key=lambda x: x['case_id'])
    return {'provisional': True, 'seed': run.get('seed'), 'error_types': types,
            'not_detected': not_detected, 'false_flags': false_flags,
            'inapplicable': inapplicable}


def _counts(mapping, order=None):
    keys = order if order is not None else sorted(mapping)
    return ', '.join(f'{k} {mapping[k]}' for k in keys if k in mapping) or 'none'


def format_failure_analysis(analysis) -> str:
    if not isinstance(analysis, dict) or 'error_types' not in analysis:
        raise ValueError('analysis must come from analyze_run')
    lines = [_HEADER, f"seed {analysis['seed']}"]
    for etype in analysis['error_types']:
        nd = analysis['not_detected'][etype]
        ff = analysis['false_flags'][etype]
        reasons = analysis['inapplicable'][etype]
        lines.append('')
        lines.append(f'error type: {etype}')
        nd_line = (f"not detected {nd['total']}"
                   if nd['total'] else 'not detected: none')
        lines.append(nd_line)
        if nd['total']:
            lines.append(f"  by stratum: {_counts(nd['by_stratum'])}")
            lines.append(f"  by condition band: {_counts(nd['by_band'], BANDS)}")
            lines.append(f"  cases: {', '.join(nd['cases'])}")
        ff_line = (f"false flags on gold claims {ff['total']}"
                   if ff['total'] else 'false flags on gold claims: none')
        lines.append(ff_line)
        if ff['total']:
            lines.append(f"  by stratum: {_counts(ff['by_stratum'])}")
            lines.append(f"  by condition band: {_counts(ff['by_band'], BANDS)}")
            lines.append('  cases: ' + ', '.join(
                f"{x['case_id']} ({', '.join(x['codes'])})" for x in ff['cases']))
        lines.append(f"inapplicable: {_counts(reasons)}")
    return '\n'.join(lines) + '\n'


def make_mentioned_blind_auditor():
    """Demo weakened auditor for failure analysis (spec 017).

    The spec-008 baseline rules with mentioned-status evidence ignored:
    mentioned gold reads as UNSUPPORTED (false flags) and missed
    mentioned codes go unreported (misses). Canned and offline; exists
    only to give the report real failures to analyze, not an auditor
    candidate.
    """
    def auditor(note_text, claimed_codes):
        states = {rec['code']: (rec['status'], rec['quote'])
                  for rec in detect_assertions(note_text)}
        upcoded = {f['code']: f for f in assess_upcoding(note_text, claimed_codes)}
        verdicts = []
        for code in claimed_codes:
            if code in upcoded:
                verdicts.append({'code': code, 'verdict': 'UNSUPPORTED',
                                 'evidence_quote': upcoded[code]['evidence_quote']})
                continue
            status, quote = states.get(code, ('absent', None))
            if status == 'affirmed':
                verdicts.append({'code': code, 'verdict': 'SUPPORTED',
                                 'evidence_quote': quote})
            elif status == 'negated':
                verdicts.append({'code': code, 'verdict': 'UNSUPPORTED',
                                 'evidence_quote': quote})
            else:
                verdicts.append({'code': code, 'verdict': 'UNSUPPORTED'})
        missed = [rec['code'] for rec in detect_assertions(note_text)
                  if rec['status'] == 'affirmed' and rec['code'] not in claimed_codes]
        return {'verdicts': verdicts, 'missed_codes': missed}
    return auditor
