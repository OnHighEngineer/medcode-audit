"""Tests for spec 028: cost accounting for the LLM regression lane."""
import json
from pathlib import Path

import pytest

from medcode_audit.regression import (REGRESSION_SEEDS, check_snapshot,
                                      load_regression_cases, run_llm_cost,
                                      run_regression)

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / 'data' / 'regression' / 'llm-cost-snapshot.json'
SUMMARY_FIELDS = ('calls', 'total_latency', 'mean_latency',
                  'prompt_chars', 'reply_chars')


def cases():
    return load_regression_cases(ROOT / 'data' / 'synthetic')


def test_validation():
    with pytest.raises(ValueError):
        run_llm_cost('not-a-list')
    with pytest.raises(ValueError):
        run_llm_cost([{'id': 'x'}, 'nope'])
    with pytest.raises(ValueError):
        run_llm_cost(cases(), seeds='0')
    with pytest.raises(ValueError):
        run_llm_cost(cases(), seeds=[0, '1'])


def test_summary_shape_and_sanity():
    out = run_llm_cost(cases(), seeds=(0,))
    assert out['case_count'] == 50
    summary = out['seeds']['0']
    assert tuple(summary) == SUMMARY_FIELDS
    assert summary['calls'] > 0
    assert summary['total_latency'] == summary['calls']
    assert summary['mean_latency'] == 1
    assert summary['prompt_chars'] > 0 and summary['reply_chars'] > 0


def test_deterministic():
    assert run_llm_cost(cases()) == run_llm_cost(cases())


def test_matches_committed_snapshot():
    live = run_llm_cost(cases())
    expected = json.loads(SNAPSHOT.read_text())
    assert check_snapshot(live, expected) == []


def test_tally_lane_untouched():
    # cost accounting lives beside the run: the spec-024 tally shape is unchanged
    out = run_regression(cases(), lane='llm')
    for seed in out['seeds'].values():
        assert 'calls' not in seed and 'prompt_chars' not in seed
