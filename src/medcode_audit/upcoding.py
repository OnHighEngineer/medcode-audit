"""Upcoding detection for ordinal families. See docs/specs/015-upcoding-ordinal.md.

A finding fires when a claimed code's title-derived severity rank exceeds the
rank the note's evidence supports (spec-011 detector, affirmed or mentioned
status only). Ranks come from the official ICD-10-CM titles via the day-15
license-safe table; non-ordinal families and unspecified codes are never
assessed. Deterministic, offline, provisional.
"""
from __future__ import annotations

from .assertions import detect_assertions
from .icd10_table import TABLE

_SUPPORTING = ('affirmed', 'mentioned')


def assess_upcoding(note_text, claimed_codes) -> list:
    if not isinstance(note_text, str):
        raise ValueError('note_text must be a string')
    if (not isinstance(claimed_codes, list)
            or any(not isinstance(c, str) for c in claimed_codes)):
        raise ValueError('claimed_codes must be a list of strings')
    supported = [rec for rec in detect_assertions(note_text)
                 if rec['status'] in _SUPPORTING]
    findings = []
    for code in claimed_codes:
        entry = TABLE.get(code)
        if entry is None or entry['rank'] is None:
            continue
        for rec in supported:
            supported_entry = TABLE.get(rec['code'])
            if (supported_entry is None
                    or supported_entry['category'] != entry['category']
                    or supported_entry['rank'] is None):
                continue
            if entry['rank'] > supported_entry['rank']:
                findings.append({'code': code,
                                 'supported_code': rec['code'],
                                 'claimed_rank': entry['rank'],
                                 'supported_rank': supported_entry['rank'],
                                 'evidence_quote': rec['quote'],
                                 'span': rec['span']})
    return findings
