"""Label review prep. See docs/specs/006-label-review-prep.md.

Deterministic stratified sampler, a JSON review sheet a human marks per gold
label, and agreement bookkeeping. No clinical judgment is automated and all
labels stay provisional until the milestone 6 human review is recorded.
"""
from __future__ import annotations

import json
from pathlib import Path

SHEET_NAME = 'medcode-audit-label-review'
SHEET_VERSION = 1
MARKS = ('agree', 'disagree')

_MARKERS = (('A', 'Confirmed diagnosis:'),
            ('N', 'Condition explicitly absent:'),
            ('U', 'Possible diagnosis, not confirmed:'))
_ROW_KEYS = {'case_id', 'gold_code', 'evidence_quote', 'reviewer_mark',
             'reviewer_note'}


def _check_cases(cases):
    if not isinstance(cases, list):
        raise ValueError('cases must be a list')
    seen = set()
    for c in cases:
        if not isinstance(c, dict):
            raise ValueError('each case must be a dict')
        cid, note = c.get('id'), c.get('note_text')
        if not isinstance(cid, str) or not cid:
            raise ValueError('each case needs a nonempty string id')
        if not isinstance(note, str):
            raise ValueError('each case needs a string note_text')
        if cid in seen:
            raise ValueError(f'duplicate case id: {cid}')
        seen.add(cid)
    return cases


def stratum_key(case) -> str:
    if not isinstance(case, dict) or not isinstance(case.get('note_text'), str):
        raise ValueError('case must be a dict with a string note_text')
    note = case['note_text']
    letters = ''.join(letter for letter, marker in _MARKERS if marker in note)
    return letters or 'none'


def sample_cases(cases, size, seed=0) -> list:
    _check_cases(cases)
    if type(size) is not int or not 1 <= size <= len(cases):
        raise ValueError('size must be an int between 1 and len(cases)')
    if type(seed) is not int:
        raise ValueError('seed must be an int')
    strata = {}
    for c in sorted(cases, key=lambda c: c['id']):
        strata.setdefault(stratum_key(c), []).append(c)
    order = sorted(strata)
    rotated, index = {}, {}
    for key in order:
        members = strata[key]
        offset = seed % len(members)
        rotated[key] = members[offset:] + members[:offset]
        index[key] = 0
    picks = []
    while len(picks) < size:
        for key in order:
            if index[key] < len(rotated[key]):
                picks.append(rotated[key][index[key]])
                index[key] += 1
                if len(picks) == size:
                    break
    return picks


def build_review_sheet(cases) -> dict:
    _check_cases(cases)
    rows = []
    for c in cases:
        gold = c.get('gold_codes') or []
        if not isinstance(gold, list):
            raise ValueError('gold_codes must be a list')
        if not gold:
            rows.append({'case_id': c['id'], 'gold_code': None,
                         'evidence_quote': None, 'reviewer_mark': None,
                         'reviewer_note': ''})
        for entry in gold:
            if (not isinstance(entry, dict)
                    or not isinstance(entry.get('code'), str)
                    or not isinstance(entry.get('evidence_quote'), str)):
                raise ValueError('each gold entry needs string code and evidence_quote')
            rows.append({'case_id': c['id'], 'gold_code': entry['code'],
                         'evidence_quote': entry['evidence_quote'],
                         'reviewer_mark': None, 'reviewer_note': ''})
    return {'sheet': SHEET_NAME, 'version': SHEET_VERSION, 'provisional': True,
            'rows': rows}


def validate_sheet(sheet) -> dict:
    if not isinstance(sheet, dict):
        raise ValueError('sheet must be a dict')
    if sheet.get('sheet') != SHEET_NAME:
        raise ValueError('unknown sheet name')
    if sheet.get('version') != SHEET_VERSION:
        raise ValueError('unknown sheet version')
    if sheet.get('provisional') is not True:
        raise ValueError('sheet must stay provisional')
    rows = sheet.get('rows')
    if not isinstance(rows, list):
        raise ValueError('rows must be a list')
    for row in rows:
        if not isinstance(row, dict) or set(row) != _ROW_KEYS:
            raise ValueError('each row needs exactly the five row keys')
        if not isinstance(row['case_id'], str) or not row['case_id']:
            raise ValueError('case_id must be a nonempty string')
        code, quote = row['gold_code'], row['evidence_quote']
        if (code is None) != (quote is None):
            raise ValueError('gold_code and evidence_quote are both null or both set')
        if code is not None and (not isinstance(code, str)
                                 or not isinstance(quote, str)):
            raise ValueError('gold_code and evidence_quote must be strings')
        if row['reviewer_mark'] is not None and row['reviewer_mark'] not in MARKS:
            raise ValueError(f'reviewer_mark must be one of {MARKS}')
        if not isinstance(row['reviewer_note'], str):
            raise ValueError('reviewer_note must be a string')
    return sheet


def dump_sheet(sheet) -> str:
    validate_sheet(sheet)
    return json.dumps(sheet, indent=2, sort_keys=True) + '\n'


def load_sheet(text) -> dict:
    if not isinstance(text, str):
        raise ValueError('sheet text must be a string')
    try:
        sheet = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f'invalid sheet JSON: {exc}') from exc
    return validate_sheet(sheet)


def summarize_review(sheet) -> dict:
    validate_sheet(sheet)
    rows = sheet['rows']
    reviewed = [r for r in rows if r['reviewer_mark'] is not None]
    disagreed = [r for r in reviewed if r['reviewer_mark'] == 'disagree']
    return {'total_rows': len(rows),
            'reviewed': len(reviewed),
            'unreviewed': len(rows) - len(reviewed),
            'agree': sum(1 for r in reviewed if r['reviewer_mark'] == 'agree'),
            'disagree': len(disagreed),
            'disagreements': [{'case_id': r['case_id'],
                               'gold_code': r['gold_code'],
                               'reviewer_note': r['reviewer_note']}
                              for r in disagreed]}

_SUMMARY_KEYS = {'total_rows', 'reviewed', 'unreviewed', 'agree', 'disagree',
                 'disagreements'}


def format_review_summary(summary) -> str:
    """Render a spec-006 summary dict as deterministic plain text (spec 040)."""
    if not isinstance(summary, dict) or set(summary) != _SUMMARY_KEYS:
        raise ValueError(f'summary must have exactly {_SUMMARY_KEYS}')
    for key in ('total_rows', 'reviewed', 'unreviewed', 'agree', 'disagree'):
        if type(summary[key]) is not int or summary[key] < 0:
            raise ValueError(f'{key} must be an int >= 0')
    disagreements = summary['disagreements']
    if not isinstance(disagreements, list):
        raise ValueError('disagreements must be a list')
    for d in disagreements:
        if (not isinstance(d, dict)
                or set(d) != {'case_id', 'gold_code', 'reviewer_note'}
                or not isinstance(d['case_id'], str)
                or not (d['gold_code'] is None
                        or isinstance(d['gold_code'], str))
                or not isinstance(d['reviewer_note'], str)):
            raise ValueError('bad disagreement row')
    lines = [
        'LABEL REVIEW SUMMARY (PROVISIONAL): counts only; disagreements are',
        'fixed via a logged decision-log entry.',
        '',
        f'total rows: {summary["total_rows"]}',
        f'reviewed: {summary["reviewed"]}',
        f'unreviewed: {summary["unreviewed"]}',
        f'agree: {summary["agree"]}',
        f'disagree: {summary["disagree"]}',
        '',
    ]
    if not disagreements:
        lines.append('disagreements: none')
    else:
        lines.append('disagreements:')
        for d in disagreements:
            code = d['gold_code'] if d['gold_code'] is not None else 'control'
            line = f'- {d["case_id"]} [{code}]'
            if d['reviewer_note']:
                line += f' {d["reviewer_note"]}'
            lines.append(line)
    return '\n'.join(lines)


def main(argv=None) -> int:
    """Print the spec-040 summary for a marked sheet; exit 0 (spec 040)."""
    args = list(argv) if argv is not None else []
    if len(args) != 1:
        raise ValueError(f'expected one sheet path, got {args}')
    path = Path(args[0])
    if not path.is_file():
        raise ValueError(f'not a file: {path}')
    sheet = load_sheet(path.read_text())
    print(format_review_summary(summarize_review(sheet)))
    return 0


if __name__ == '__main__':
    import sys
    raise SystemExit(main(sys.argv[1:]))
