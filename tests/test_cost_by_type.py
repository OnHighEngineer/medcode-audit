"""Tests for spec 030: per-error-type cost split for the LLM lane."""
import json
from pathlib import Path

import pytest

from medcode_audit.regression import (REGRESSION_SEEDS, check_snapshot,
                                      load_regression_cases, run_llm_cost,
                                      run_llm_cost_by_type)
from medcode_audit.schema import ERROR_TYPES

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / 'data' / 'regression' / 'llm-cost-by-type-snapshot.json'
SUMMARY_FIELDS = ('calls', 'total_latency', 'mean_latency',
                  'prompt_chars', 'reply_chars')


def cases():
    return load_regression_cases(ROOT / 'data' / 'synthetic')


def test_validation():
    with pytest.raises(ValueError):
        run_llm_cost_by_type('not-a-list')
    with pytest.raises(ValueError):
        run_llm_cost_by_type([{'id': 'x'}, 'nope'])
    with pytest.raises(ValueError):
        run_llm_cost_by_type(cases(), seeds='0')
    with pytest.raises(ValueError):
        run_llm_cost_by_type(cases(), seeds=[0, '1'])


def test_shape_and_sanity():
    out = run_llm_cost_by_type(cases(), seeds=(0,))
    assert out['case_count'] == 50
    per_type = out['seeds']['0']
    assert tuple(per_type) == ERROR_TYPES
    for etype, summary in per_type.items():
        assert tuple(summary) == SUMMARY_FIELDS
        if summary['calls']:
            assert summary['total_latency'] == summary['calls']
            assert summary['mean_latency'] == 1
        else:
            assert summary['total_latency'] == 0
            assert summary['mean_latency'] is None
    # at least one type is inapplicable on every case, and at least one
    # type carries transport volume
    assert any(s['calls'] == 0 for s in per_type.values())
    assert any(s['calls'] > 0 for s in per_type.values())


def test_split_sums_to_combined_totals():
    # per-type runs ask the same (case, error type) questions as the
    # combined spec-028 run, so the split must sum to its totals
    split = run_llm_cost_by_type(cases())
    combined = run_llm_cost(cases())
    for seed in split['seeds']:
        rows = split['seeds'][seed].values()
        total = combined['seeds'][seed]
        assert sum(s['calls'] for s in rows) == total['calls']
        assert sum(s['prompt_chars'] for s in rows) == total['prompt_chars']
        assert sum(s['reply_chars'] for s in rows) == total['reply_chars']


def test_deterministic():
    assert run_llm_cost_by_type(cases()) == run_llm_cost_by_type(cases())


def test_matches_committed_snapshot():
    live = run_llm_cost_by_type(cases())
    expected = json.loads(SNAPSHOT.read_text())
    assert check_snapshot(live, expected) == []
