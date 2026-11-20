"""Tests for spec 034: self-check lanes for the committed demo artifacts."""
import shutil
from pathlib import Path

import pytest

from medcode_audit.regression import (SELF_CHECK_LANES,
                                      check_committed_snapshots)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
REVIEWS = ROOT / 'docs' / 'reviews'


def _copy_reviews(tmp_path):
    reviews = tmp_path / 'reviews'
    reviews.mkdir()
    for name in ('day-27-demo-output.md', 'day-29-demo-report.html'):
        shutil.copy(REVIEWS / name, reviews / name)
    return reviews


def test_artifact_lanes_appended_and_ok():
    assert SELF_CHECK_LANES[-2:] == ('demo_report', 'demo_html')
    results = check_committed_snapshots()
    assert tuple(results) == SELF_CHECK_LANES
    assert results['demo_report'] == []
    assert results['demo_html'] == []


def test_artifact_drift_names_file_and_first_line(tmp_path):
    reviews = _copy_reviews(tmp_path)
    artifact = reviews / 'day-29-demo-report.html'
    artifact.write_text(artifact.read_text() + '<!-- tampered -->\n')
    results = check_committed_snapshots(reviews_dir=reviews)
    assert results['demo_html'] != []
    assert any('day-29-demo-report.html' in p for p in results['demo_html'])
    assert results['demo_report'] == []
    for lane in SELF_CHECK_LANES[:7]:
        assert results[lane] == [], lane


def test_missing_artifact_raises(tmp_path):
    reviews = _copy_reviews(tmp_path)
    (reviews / 'day-27-demo-output.md').unlink()
    with pytest.raises(ValueError):
        check_committed_snapshots(reviews_dir=reviews)
