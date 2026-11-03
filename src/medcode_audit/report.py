"""Report generator (markdown v1). See docs/specs/019-report-generator.md.

Assembles one markdown eval report from the spec-005 run, the spec-017
failure analysis and the spec-018 cost/latency records. The generator
owns the title, provisional header and seed line; section bodies are the
frozen module formatters embedded verbatim. Deterministic, no
percentages, no HTML in v1.
"""
from __future__ import annotations

from .cost_latency import format_cost_latency, summarize_records
from .failure_analysis import format_failure_analysis
from .runner import format_report

_HEADER = ('EVAL REPORT (PROVISIONAL): synthetic labels, no clinical review '
           'yet (milestone 6). Counts only, not trusted scores.')


def _check_run(run):
    if not isinstance(run, dict):
        raise ValueError('run must be a dict')
    if type(run.get('seed')) is not int:
        raise ValueError('run needs an int seed')
    if not isinstance(run.get('results'), list):
        raise ValueError('run needs a list results')
    if not isinstance(run.get('tally'), dict):
        raise ValueError('run needs a dict tally')
    return run


def _check_analysis(analysis, run):
    if not isinstance(analysis, dict) or not isinstance(analysis.get('error_types'), list):
        raise ValueError('analysis must come from analyze_run')
    if analysis['error_types'] != list(run['tally']):
        raise ValueError('analysis error types must match the run tally order')
    if analysis.get('seed') != run['seed']:
        raise ValueError('analysis seed must match the run seed')
    return analysis


def generate_report(run, analysis=None, cost_records=None) -> str:
    _check_run(run)
    sections = ['# medcode-audit eval report', '', _HEADER, '',
                f"seed {run['seed']}", '',
                '## Runner summary', '', '```', format_report(run).rstrip('\n'),
                '```']
    if analysis is not None:
        _check_analysis(analysis, run)
        sections += ['', '## Failure analysis', '', '```',
                     format_failure_analysis(analysis).rstrip('\n'), '```']
    if cost_records is not None:
        summarize_records(cost_records)  # spec-018 record validation
        sections += ['', '## Cost/latency', '', '```',
                     format_cost_latency(cost_records).rstrip('\n'), '```']
    return '\n'.join(sections) + '\n'
