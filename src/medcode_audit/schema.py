"""Synthetic case schema and loader. See docs/specs/001-case-schema.md and
   docs/specs/020-case-schema-v2.md (optional procedure codes, vocabulary-neutral)."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

ERROR_TYPES = (
    "wrong_code",
    "upcoding",
    "unsupported_code",
    "missed_code",
    "negated_condition",
)
_CODE_RE = re.compile(r"^[A-Z][0-9]{2}(\.[A-Z0-9]{1,4})?$")
_PROC_CODE_RE = re.compile(r"^[A-Z0-9]{4,7}$")


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
    procedure_codes: list = field(default_factory=list)


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
    procedures = []
    if "procedure_codes" in d:
        raw_procs = d["procedure_codes"]
        if not isinstance(raw_procs, list):
            raise CaseValidationError("procedure_codes must be a list")
        for item in raw_procs:
            if not isinstance(item, dict):
                raise CaseValidationError("procedure_codes item must be an object")
            code = item.get("code")
            if not isinstance(code, str) or not _PROC_CODE_RE.match(code):
                raise CaseValidationError(f"procedure_codes code malformed: {code!r}")
            quote = item.get("evidence_quote")
            if not isinstance(quote, str) or not quote:
                raise CaseValidationError(f"procedure_codes evidence_quote missing for {code}")
            if quote not in note:
                raise CaseValidationError(
                    f"procedure_codes evidence_quote not found in note for {code}")
            procedures.append(GoldCode(code, quote))
    errors = _need(d, "injected_errors")
    if not isinstance(errors, list) or any(e not in ERROR_TYPES for e in errors):
        raise CaseValidationError(f"injected_errors must be a list of {ERROR_TYPES}")
    return Case(case_id, True, note, codes, list(errors), procedures)


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
