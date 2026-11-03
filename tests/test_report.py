"""Frozen tests for spec 019: report generator (markdown v1)."""
import json

import pytest

from medcode_audit.cost_latency import make_tracking_transport
from medcode_audit.failure_analysis import analyze_run, format_failure_analysis
from medcode_audit.goldset import build_gold_cases
from medcode_audit.llm_auditor import make_llm_auditor
from medcode_audit.report import generate_report
from medcode_audit.runner import format_report, run_eval

HEADER = ('EVAL REPORT (PROVISIONAL): synthetic labels, no clinical review '
          'yet (milestone 6). Counts only, not trusted scores.')


def _unsupported_reply(prompt):
    claimed = json.loads(prompt.split('CLAIMED_CODES_JSON:\n')[1].split('\n')[0])
    return json.dumps({'verdicts': [{'code': c, 'verdict': 'UNSUPPORTED'}
                                    for c in claimed],
                       'missed_codes': []})


def tracked_run(n=6):
    batch = build_gold_cases(n)
    tracked, records = make_tracking_transport(_unsupported_reply,
                                               iter(range(10**6)).__next__)
    run = run_eval(batch, make_llm_auditor(tracked), seed=0)
    return batch, run, records


def test_run_only_report():
    _, run, _ = tracked_run()
    out = generate_report(run)
    assert out.startswith('# medcode-audit eval report\n')
    assert HEADER in out
    assert 'seed 0' in out
    assert '## Runner summary' in out
    assert format_report(run) in out
    assert '## Failure analysis' not in out
    assert '## Cost/latency' not in out
    assert '%' not in out
    assert out == generate_report(run)  # deterministic


def test_full_report_embeds_each_artifact_verbatim():
    batch, run, records = tracked_run()
    analysis = analyze_run(run, batch)
    out = generate_report(run, analysis, records)
    assert format_report(run) in out
    assert format_failure_analysis(analysis) in out
    assert '## Cost/latency' in out
    assert f'calls {len(records)}' in out
    assert '%' not in out
    assert out == generate_report(run, analysis, list(records))


def test_empty_cost_records_render_honest_zero():
    _, run, _ = tracked_run()
    out = generate_report(run, cost_records=[])
    assert '## Cost/latency' in out
    assert 'no calls recorded' in out


def test_analysis_must_match_the_run():
    batch, run, _ = tracked_run()
    analysis = analyze_run(run, batch)
    other = dict(analysis, seed=99)
    with pytest.raises(ValueError):
        generate_report(run, other)
    trimmed = dict(analysis, error_types=analysis['error_types'][:-1])
    with pytest.raises(ValueError):
        generate_report(run, trimmed)
    with pytest.raises(ValueError):
        generate_report(run, {'not': 'an analysis'})


@pytest.mark.parametrize('run', [None, 'x', {}, {'seed': 0},
                                 {'seed': '0', 'results': [], 'tally': {}},
                                 {'seed': 0, 'results': 'x', 'tally': {}},
                                 {'seed': 0, 'results': [], 'tally': []}])
def test_bad_run_rejected(run):
    with pytest.raises(ValueError):
        generate_report(run)


def test_bad_cost_records_rejected():
    _, run, _ = tracked_run()
    with pytest.raises(ValueError):
        generate_report(run, cost_records=[{'call': 0, 'prompt_chars': 1,
                                            'reply_chars': 1, 'latency': 1}])
