"""ICD-10 code lookup tool. See docs/specs/012-code-lookup.md.

License-safe, offline, deterministic: answers from the small hand-checked
table in icd10_table.py, never from a guess. Unknown codes fail closed with
LookupError; malformed codes fail with ValueError. No severity ordering is
recorded or implied anywhere in this module.
"""
from __future__ import annotations

import re

from .icd10_table import TABLE

_SHAPE = re.compile(r'^[A-Z]\d{2}(\.\d{1,4})?$')


def _normalize(code):
    if not isinstance(code, str):
        raise ValueError('code must be a string')
    normalized = code.strip().upper()
    if not _SHAPE.match(normalized):
        raise ValueError(f'not an ICD-10 code shape: {code!r}')
    return normalized


def lookup(code) -> dict:
    """Return a fresh copy of the table entry for code, or fail closed."""
    normalized = _normalize(code)
    if normalized not in TABLE:
        raise LookupError(f'code not in the checked-in table: {normalized}')
    entry = dict(TABLE[normalized])
    entry['family'] = family(normalized)
    return entry


def is_known(code) -> bool:
    """True when lookup(code) would succeed; never raises."""
    try:
        lookup(code)
    except (ValueError, LookupError):
        return False
    return True


def known_codes() -> tuple:
    return tuple(sorted(TABLE))


def family(code) -> tuple:
    """Sorted codes in the table sharing the code's 3-character category."""
    normalized = _normalize(code)
    if normalized not in TABLE:
        raise LookupError(f'code not in the checked-in table: {normalized}')
    category = TABLE[normalized]['category']
    return tuple(sorted(c for c, row in TABLE.items()
                        if row['category'] == category))
