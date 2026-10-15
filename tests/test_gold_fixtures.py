import json
from pathlib import Path

from medcode_audit.goldset import build_gold_cases
from medcode_audit.schema import load_cases

ROOT = Path(__file__).resolve().parents[1]


def test_combined_fifty_unique_cases():
    cases = load_cases(ROOT / 'data/synthetic')
    assert len(cases) == len({c.id for c in cases}) == 50


def test_checked_in_assertion_batch_is_reproducible():
    for expected in build_gold_cases():
        path = ROOT / 'data/synthetic' / (expected['id'] + '.json')
        assert json.loads(path.read_text()) == expected
