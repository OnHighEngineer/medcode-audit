from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_required_docs_exist():
    for f in ["README.md", "docs/specs/000-product-spec.md", "docs/plans/2026-10-13-30-day-plan.md", "docs/brainstorms/2026-10-13-day1-brainstorm.md", "docs/plans/2026-10-13-day-01-plan.md", "decision-log.md", "flow.md", "AGENTS.md", "SESSION.md"]:
        assert (ROOT / f).exists(), f


def test_decision_log_entries_have_three_parts():
    text = (ROOT / "decision-log.md").read_text()
    entries = [e for e in text.split("### ")[1:]]
    assert entries
    for e in entries:
        assert "**Chose:**" in e and "**Why:**" in e and "**Rejected" in e
