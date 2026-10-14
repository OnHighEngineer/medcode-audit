import copy
import json
from pathlib import Path

import pytest

from medcode_audit.schema import CaseValidationError, load_case, load_cases, parse_case

ROOT = Path(__file__).resolve().parents[1]

VALID = {
    "id": "case-x",
    "synthetic": True,
    "note_text": "SYNTHETIC. Patient has type 2 diabetes without complications. BP stable.",
    "gold_codes": [
        {"code": "E11.9", "evidence_quote": "type 2 diabetes without complications"}
    ],
    "injected_errors": [],
}


def make(**changes):
    d = copy.deepcopy(VALID)
    d.update(changes)
    return d


def test_accepts_valid_case():
    case = parse_case(make())
    assert case.id == "case-x"
    assert case.synthetic is True
    assert case.gold_codes[0].code == "E11.9"
    assert case.injected_errors == []


def test_rejects_missing_synthetic_flag():
    d = make()
    del d["synthetic"]
    with pytest.raises(CaseValidationError, match="synthetic"):
        parse_case(d)


@pytest.mark.parametrize("bad", [False, "true", 1, None])
def test_rejects_non_true_synthetic(bad):
    with pytest.raises(CaseValidationError, match="synthetic"):
        parse_case(make(synthetic=bad))


def test_rejects_gold_code_without_evidence_quote():
    d = make(gold_codes=[{"code": "E11.9"}])
    with pytest.raises(CaseValidationError, match="evidence_quote"):
        parse_case(d)


def test_rejects_empty_evidence_quote():
    d = make(gold_codes=[{"code": "E11.9", "evidence_quote": ""}])
    with pytest.raises(CaseValidationError, match="evidence_quote"):
        parse_case(d)


def test_rejects_evidence_quote_not_in_note():
    d = make(gold_codes=[{"code": "E11.9", "evidence_quote": "asthma flare"}])
    with pytest.raises(CaseValidationError, match="evidence_quote"):
        parse_case(d)


@pytest.mark.parametrize("bad", ["", "11.9", "E1", "E11.99999", "e11.9", "E11,9"])
def test_rejects_malformed_code(bad):
    d = make(gold_codes=[{"code": bad, "evidence_quote": "type 2 diabetes"}])
    with pytest.raises(CaseValidationError, match="code"):
        parse_case(d)


def test_rejects_unknown_error_type():
    with pytest.raises(CaseValidationError, match="injected_errors"):
        parse_case(make(injected_errors=["made_up"]))


def test_accepts_known_error_types():
    errs = ["wrong_code", "upcoding", "unsupported_code", "missed_code", "negated_condition"]
    assert parse_case(make(injected_errors=errs)).injected_errors == errs


@pytest.mark.parametrize("field", ["id", "note_text", "gold_codes", "injected_errors"])
def test_rejects_missing_required_field(field):
    d = make()
    del d[field]
    with pytest.raises(CaseValidationError, match=field):
        parse_case(d)


def test_rejects_empty_id_and_note():
    with pytest.raises(CaseValidationError, match="id"):
        parse_case(make(id=""))
    with pytest.raises(CaseValidationError, match="note_text"):
        parse_case(make(note_text="  "))


def test_load_case_reads_file(tmp_path):
    p = tmp_path / "a.json"
    p.write_text(json.dumps(VALID))
    assert load_case(p).id == "case-x"


def test_load_cases_rejects_duplicate_ids(tmp_path):
    for name in ("a.json", "b.json"):
        (tmp_path / name).write_text(json.dumps(VALID))
    with pytest.raises(CaseValidationError, match="duplicate"):
        load_cases(tmp_path)


def test_load_cases_sorted_by_filename(tmp_path):
    (tmp_path / "b.json").write_text(json.dumps(make(id="b")))
    (tmp_path / "a.json").write_text(json.dumps(make(id="a")))
    assert [c.id for c in load_cases(tmp_path)] == ["a", "b"]


def test_repo_synthetic_cases_are_valid():
    cases = load_cases(ROOT / "data" / "synthetic")
    assert len(cases) >= 3
    assert all(c.synthetic for c in cases)
