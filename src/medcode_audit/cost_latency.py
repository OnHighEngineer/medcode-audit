"""Cost/latency tracking at the transport boundary. See docs/specs/018-cost-latency.md.

Wraps a spec-009 transport(prompt) -> reply_text with per-call
accounting: prompt/reply size in characters (the offline unit, no
tokenizer) and latency measured by an injected clock, so the suite stays
deterministic and no live provider is needed. Records stay beside the
frozen spec-005 run shape, never inside it. All numbers provisional.
"""
from __future__ import annotations

_HEADER = ('COST/LATENCY (PROVISIONAL): character counts and transport '
           'timings at the spec-009 boundary; synthetic accounting only, '
           'not trusted scores.')

_RECORD_KEYS = {'call', 'prompt_chars', 'reply_chars', 'latency'}


def _is_number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def make_tracking_transport(transport, clock):
    if not callable(transport):
        raise ValueError('transport must be callable')
    if not callable(clock):
        raise ValueError('clock must be callable')
    records = []

    def tracked(prompt):
        if not isinstance(prompt, str):
            raise ValueError('prompt must be a string')
        start = clock()
        if not _is_number(start):
            raise ValueError('clock must return a number')
        reply = transport(prompt)
        end = clock()
        if not _is_number(end):
            raise ValueError('clock must return a number')
        if end < start:
            raise ValueError('clock went backwards')
        if not isinstance(reply, str):
            raise ValueError('transport must return a string reply')
        records.append({'call': len(records) + 1,
                        'prompt_chars': len(prompt),
                        'reply_chars': len(reply),
                        'latency': end - start})
        return reply

    return tracked, records


def _check_records(records):
    if not isinstance(records, list):
        raise ValueError('records must be a list')
    for r in records:
        if not isinstance(r, dict) or set(r) != _RECORD_KEYS:
            raise ValueError(f'each record needs exactly {sorted(_RECORD_KEYS)}')
        if type(r['call']) is not int or r['call'] < 1:
            raise ValueError('call must be an int >= 1')
        for key in ('prompt_chars', 'reply_chars'):
            if type(r[key]) is not int or r[key] < 0:
                raise ValueError(f'{key} must be an int >= 0')
        if not _is_number(r['latency']) or r['latency'] < 0:
            raise ValueError('latency must be a number >= 0')
    return records


def summarize_records(records) -> dict:
    _check_records(records)
    calls = len(records)
    total_latency = sum(r['latency'] for r in records)
    return {'calls': calls,
            'total_latency': total_latency,
            'mean_latency': (total_latency / calls) if calls else None,
            'prompt_chars': sum(r['prompt_chars'] for r in records),
            'reply_chars': sum(r['reply_chars'] for r in records)}


def format_cost_latency(records) -> str:
    s = summarize_records(records)
    lines = [_HEADER, f"calls {s['calls']}"]
    if not s['calls']:
        lines.append('no calls recorded')
    else:
        lines.append(f"latency: total {s['total_latency']}, mean {s['mean_latency']}")
        lines.append(f"characters: prompt {s['prompt_chars']} in, "
                     f"reply {s['reply_chars']} out")
    return '\n'.join(lines) + '\n'
