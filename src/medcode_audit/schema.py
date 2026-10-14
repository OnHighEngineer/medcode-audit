"""Synthetic case schema and loader. See docs/specs/001-case-schema.md."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

ERROR_TYPES = (
    "wrong_code",
    "upcoding",
    "unsupported_code",
    "missed_code",
    "negated_condition",
)
_CODE_RE = re.compile(r"^[A-Z][0-9]{2}(\.[A-Z0-9]{1,4})?$")


class CaseValidationError(ValueError):
    """Raised when a case does not match the schema."""


@dataclass(frozen=True)
class GoldCode:
    code: str
    evidence_quote: str


@dataclass(frozen=True)
class Case:
    id: str
    synthetic: bool
    note_text: str
    gold_codes: list
    injected_errors: list


def _need(d, field):
    if field not in d:
        raise CaseValidationError(f"missing field: {field}")
    return d[field]


def _text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise CaseValidationError(f"{field} must be a non-empty string")
    return value


def parse_case(d) -> Case:
    if not isinstance(d, dict):
        raise CaseValidationError("case must be an object")
    case_id = _text(_need(d, "id"), "id")
    if _need(d, "synthetic") is not True:
        raise CaseValidationError("synthetic must be true")
    note = _text(_need(d, "note_text"), "note_text")
    raw_codes = _need(d, "gold_codes")
    if not isinstance(raw_codes, list):
        raise CaseValidationError("gold_codes must be a list")
    codes = []
    for item in raw_codes:
        if not isinstance(item, dict):
            raise CaseValidationError("gold_codes item must be an object")
        code = item.get("code")
        if not isinstance(code, str) or not _CODE_RE.match(code):
            raise CaseValidationError(f"gold_codes code malformed: {code!r}")
        quote = item.get("evidence_quote")
        if not isinstance(quote, str) or not quote:
            raise CaseValidationError(f"gold_codes evidence_quote missing for {code}")
        if quote not in note:
            raise CaseValidationError(f"gold_codes evidence_quote not found in note for {code}")
        codes.append(GoldCode(code, quote))
    errors = _need(d, "injected_errors")
    if not isinstance(errors, list) or any(e not in ERROR_TYPES for e in errors):
        raise CaseValidationError(f"injected_errors must be a list of {ERROR_TYPES}")
    return Case(case_id, True, note, codes, list(errors))


def load_case(path) -> Case:
    return parse_case(json.loads(Path(path).read_text()))


def load_cases(directory) -> list:
    cases, seen = [], set()
    for p in sorted(Path(directory).glob("*.json")):
        case = load_case(p)
        if case.id in seen:
            raise CaseValidationError(f"duplicate id: {case.id}")
        seen.add(case.id)
        cases.append(case)
    return cases
