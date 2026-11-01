"""Frozen tests for spec 018: cost/latency tracking at the transport boundary."""
import copy
import json

import pytest

from medcode_audit.cost_latency import (format_cost_latency,
                                        make_tracking_transport,
                                        summarize_records)
from medcode_audit.goldset import build_gold_cases
from medcode_audit.llm_auditor import make_llm_auditor, static_transport
from medcode_audit.runner import run_eval

HEADER = ('COST/LATENCY (PROVISIONAL): character counts and transport '
          'timings at the spec-009 boundary; synthetic accounting only, '
          'not trusted scores.')


def clock_from(values):
    it = iter(values)
    return lambda: next(it)


def test_make_tracking_transport_validates_callables():
    with pytest.raises(ValueError):
        make_tracking_transport('not callable', lambda: 0)
    with pytest.raises(ValueError):
        make_tracking_transport(static_transport('x'), 'not callable')


def test_records_each_call_in_order():
    reply = '{"verdicts": [], "missed_codes": []}'
    tracked, records = make_tracking_transport(static_transport(reply),
                                               clock_from([10, 12, 20, 25]))
    assert tracked('abc') == reply
    assert tracked('de') == reply
    assert records == [{'call': 1, 'prompt_chars': 3, 'reply_chars': len(reply), 'latency': 2},
                       {'call': 2, 'prompt_chars': 2, 'reply_chars': len(reply), 'latency': 5}]


def test_prompt_must_be_string():
    tracked, _ = make_tracking_transport(static_transport('ok'), clock_from([0]))
    with pytest.raises(ValueError):
        tracked(42)


def test_clock_must_return_numbers_not_bools():
    tracked, _ = make_tracking_transport(static_transport('ok'), clock_from(['x']))
    with pytest.raises(ValueError):
        tracked('p')
    tracked, _ = make_tracking_transport(static_transport('ok'), clock_from([True]))
    with pytest.raises(ValueError):
        tracked('p')
    tracked, _ = make_tracking_transport(static_transport('ok'), clock_from([0, True]))
    with pytest.raises(ValueError):
        tracked('p')


def test_clock_must_not_go_backwards():
    tracked, _ = make_tracking_transport(static_transport('ok'), clock_from([5, 4]))
    with pytest.raises(ValueError):
        tracked('p')


def test_transport_must_return_string():
    tracked, _ = make_tracking_transport(lambda prompt: 42, clock_from([0, 1]))
    with pytest.raises(ValueError):
        tracked('p')


def test_summarize_records():
    s = summarize_records([{'call': 1, 'prompt_chars': 10, 'reply_chars': 4, 'latency': 2},
                           {'call': 2, 'prompt_chars': 6, 'reply_chars': 8, 'latency': 4}])
    assert s == {'calls': 2, 'total_latency': 6, 'mean_latency': 3.0,
                 'prompt_chars': 16, 'reply_chars': 12}
    empty = summarize_records([])
    assert empty['calls'] == 0 and empty['mean_latency'] is None


@pytest.mark.parametrize('bad', [
    'x', [1], [{'call': 0, 'prompt_chars': 1, 'reply_chars': 1, 'latency': 1}],
    [{'call': 1, 'prompt_chars': -1, 'reply_chars': 1, 'latency': 1}],
    [{'call': 1, 'prompt_chars': 1, 'reply_chars': True, 'latency': 1}],
    [{'call': 1, 'prompt_chars': 1, 'reply_chars': 1, 'latency': -0.5}],
    [{'call': 1, 'prompt_chars': 1, 'reply_chars': 1}],
])
def test_summarize_records_rejects_bad_input(bad):
    with pytest.raises(ValueError):
        summarize_records(bad)


def test_format_is_deterministic_and_provisional():
    records = [{'call': 1, 'prompt_chars': 10, 'reply_chars': 4, 'latency': 2},
               {'call': 2, 'prompt_chars': 6, 'reply_chars': 8, 'latency': 4}]
    a = format_cost_latency(records)
    assert a == format_cost_latency(copy.deepcopy(records))
    assert a.startswith(HEADER)
    assert '%' not in a
    assert 'calls 2' in a
    assert 'total 6' in a and 'mean 3.0' in a
    assert 'prompt 16 in' in a and 'reply 12 out' in a
    empty = format_cost_latency([])
    assert empty.startswith(HEADER)
    assert 'no calls recorded' in empty


def _unsupported_reply_transport(prompt):
    claimed = json.loads(prompt.split('CLAIMED_CODES_JSON:\n')[1].split('\n')[0])
    return json.dumps({'verdicts': [{'code': c, 'verdict': 'UNSUPPORTED'}
                                    for c in claimed],
                       'missed_codes': []})


def test_eval_integration_records_one_call_per_applicable_row():
    batch = build_gold_cases(6)
    tracked, records = make_tracking_transport(_unsupported_reply_transport,
                                               clock_from(range(1000)))
    run = run_eval(batch, make_llm_auditor(tracked), seed=0)
    assert set(run) == {'provisional', 'seed', 'results', 'tally'}  # run shape frozen
    applicable = sum(t['applicable'] for t in run['tally'].values())
    assert len(records) == applicable
    assert [r['call'] for r in records] == list(range(1, applicable + 1))
    assert all(r['latency'] == 1 and r['prompt_chars'] > 0 and r['reply_chars'] > 0
               for r in records)
    summary = summarize_records(records)
    assert summary['calls'] == applicable and summary['total_latency'] == applicable
