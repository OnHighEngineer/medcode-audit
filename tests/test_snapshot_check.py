"""Tests for spec 032: snapshot self-check entry point."""
import io
import json
import shutil
from contextlib import redirect_stdout
from pathlib import Path

import pytest

from medcode_audit.regression import (SELF_CHECK_LANES,
                                      check_committed_snapshots, main)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'


def test_check_committed_snapshots_all_ok():
    results = check_committed_snapshots()
    assert tuple(results) == SELF_CHECK_LANES
    for lane in SELF_CHECK_LANES:
        assert results[lane] == [], lane


def test_check_committed_snapshots_names_drift(tmp_path):
    data = tmp_path / 'data'
    shutil.copytree(DATA / 'synthetic', data / 'synthetic')
    shutil.copytree(DATA / 'regression', data / 'regression')
    snap_path = data / 'regression' / 'baseline-snapshot.json'
    snap = json.loads(snap_path.read_text())
    snap['seeds']['0']['missed_code']['detected'] += 1
    snap_path.write_text(json.dumps(snap))
    results = check_committed_snapshots(data)
    assert results['baseline'] != []
    assert any('missed_code.detected' in p for p in results['baseline'])
    for lane in SELF_CHECK_LANES:
        if lane != 'baseline':
            assert results[lane] == [], lane


def test_check_committed_snapshots_validation(tmp_path):
    with pytest.raises(ValueError):
        check_committed_snapshots(tmp_path / 'no-such-dir')


def test_main_prints_ok_lines_and_rejects_args():
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = main()
    assert rc == 0
    assert buf.getvalue().splitlines() == [f'{lane}: OK'
                                           for lane in SELF_CHECK_LANES]
    with pytest.raises(ValueError):
        main(['--fix'])
