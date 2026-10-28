"""Missed-code findings with evidence. See docs/specs/014-missed-code-detection.md.

A missed finding is a condition the note supports (spec-011 statuses
affirmed or mentioned) that no claimed code covers, carrying the verbatim
evidence quote and span from the detector record. Deterministic and offline;
no new clinical rules.
"""
from __future__ import annotations

from .assertions import detect_assertions

_SUPPORTING = ('affirmed', 'mentioned')


def find_missed(note_text, claimed_codes) -> list:
    if not isinstance(note_text, str):
        raise ValueError('note_text must be a string')
    if (not isinstance(claimed_codes, list)
            or any(not isinstance(c, str) for c in claimed_codes)):
        raise ValueError('claimed_codes must be a list of strings')
    findings = []
    for rec in detect_assertions(note_text):
        if rec['status'] in _SUPPORTING and rec['code'] not in claimed_codes:
            findings.append({'code': rec['code'],
                             'evidence_quote': rec['quote'],
                             'span': rec['span']})
    return findings
