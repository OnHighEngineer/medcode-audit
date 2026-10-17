import copy

import pytest

from medcode_audit.goldset import build_gold_cases, make_assertion_case
from medcode_audit.runner import VERDICTS, format_report, run_eval
from medcode_audit.schema import ERROR_TYPES

IMPLEMENTED = ('missed_code', 'unsupported_code', 'negated_condition')
DEFERRED = ('upcoding', 'wrong_code')


def cases():
    return build_gold_cases(14)


def perfect(batch):
    gold = {c['note_text']: {g['code'] for g in c['gold_codes']} for c in batch}

    def auditor(note, claimed):
        g = gold[note]
        return {'verdicts': [{'code': c, 'verdict': 'SUPPORTED' if c in g else 'UNSUPPORTED'}
                             for c in claimed],
                'missed_codes': sorted(g - set(claimed))}
    return auditor


def always(verdict):
    def auditor(note, claimed):
        return {'verdicts': [{'code': c, 'verdict': verdict} for c in claimed],
                'missed_codes': []}
    return auditor


def test_verdict_names():
    assert VERDICTS == ('SUPPORTED', 'UNSUPPORTED', 'WRONG_SPECIFICITY', 'MISSED')


def test_perfect_auditor_catches_everything_with_no_false_flags():
    batch = cases()
    run = run_eval(batch, perfect(batch))
    assert run['provisional'] is True
    for etype, n in zip(IMPLEMENTED, (25, 35, 16)):
        t = run['tally'][etype]
        assert t['applicable'] == n and t['detected'] == n
        assert t['not_detected'] == 0 and t['false_flags'] == 0
        assert t['inapplicable'] == 37 - n


def test_always_supported_catches_nothing_without_false_flags():
    run = run_eval(cases(), always('SUPPORTED'))
    for etype in IMPLEMENTED:
        t = run['tally'][etype]
        assert t['detected'] == 0 and t['not_detected'] == t['applicable']
        assert t['false_flags'] == 0


def test_always_unsupported_catches_claims_but_flags_gold():
    run = run_eval(cases(), always('UNSUPPORTED'))
    assert run['tally']['unsupported_code']['detected'] == 35
    assert run['tally']['negated_condition']['detected'] == 16
    assert run['tally']['missed_code']['detected'] == 0
    assert run['tally']['unsupported_code']['false_flags'] > 0


def test_inapplicable_cases_counted_separately_and_auditor_not_called():
    calls = []

    def auditor(note, claimed):
        calls.append(claimed)
        return {'verdicts': [{'code': c, 'verdict': 'SUPPORTED'} for c in claimed],
                'missed_codes': []}
    run = run_eval(cases(), auditor, error_types=DEFERRED)
    for etype in DEFERRED:
        t = run['tally'][etype]
        assert t['applicable'] == 0 and t['inapplicable'] == 37
        assert t['reasons'] == {'deferred_unverified_mapping': 37}
    assert calls == []
    assert all(r['status'] == 'inapplicable' for r in run['results'])


def test_deterministic_and_cases_not_mutated():
    batch = cases()
    before = copy.deepcopy(batch)
    a = run_eval(batch, perfect(batch), seed=2)
    b = run_eval(copy.deepcopy(batch), perfect(batch), seed=2)
    assert a == b
    assert batch == before
    assert [r['error_type'] for r in a['results'][:5]] == list(ERROR_TYPES)


def test_auditor_sees_only_note_and_code_strings():
    seen = []

    def auditor(note, claimed):
        seen.append((note, claimed))
        return {'verdicts': [{'code': c, 'verdict': 'SUPPORTED'} for c in claimed],
                'missed_codes': []}
    run_eval(cases()[:3], auditor)
    assert seen
    for note, claimed in seen:
        assert isinstance(note, str)
        assert isinstance(claimed, list) and all(isinstance(c, str) for c in claimed)


def test_bad_inputs():
    batch = cases()[:2]
    ok = always('SUPPORTED')
    for bad in ('x', None, {}):
        with pytest.raises(ValueError):
            run_eval(bad, ok)
    with pytest.raises(ValueError):
        run_eval(batch, 'not callable')
    with pytest.raises(ValueError):
        run_eval(batch, ok, error_types=['nonsense'])
    for bad in (True, 1.5, '1'):
        with pytest.raises(ValueError):
            run_eval(batch, ok, seed=bad)


def _one_case():
    return [make_assertion_case('t-1', [('I10', 'affirmed'), ('E11.9', 'affirmed')])]


@pytest.mark.parametrize('bad', [
    None,
    [],
    {'verdicts': [], 'missed_codes': []},
    {'verdicts': [{'code': 'I10', 'verdict': 'MAYBE'}], 'missed_codes': []},
    {'verdicts': [{'code': 'I10', 'verdict': 'SUPPORTED'},
                  {'code': 'I10', 'verdict': 'SUPPORTED'}], 'missed_codes': []},
    {'verdicts': [{'code': 'I10', 'verdict': 'SUPPORTED'},
                  {'code': 'D50.9', 'verdict': 'SUPPORTED'}], 'missed_codes': []},
    {'verdicts': [{'code': 'I10', 'verdict': 'SUPPORTED'}], 'missed_codes': 'I10'},
    {'verdicts': [{'code': 'I10', 'verdict': 'SUPPORTED'}], 'missed_codes': [1]},
])
def test_malformed_auditor_output_fails_closed(bad):
    with pytest.raises(ValueError):
        run_eval(_one_case(), lambda note, claimed: bad, error_types=['missed_code'])


def test_report_is_provisional_plain_and_honest_about_deferred():
    batch = cases()
    run = run_eval(batch, perfect(batch))
    text = format_report(run)
    assert text == format_report(run)
    assert text.splitlines()[0].startswith('PROVISIONAL')
    assert '%' not in text
    for etype in IMPLEMENTED:
        assert any(l.startswith(etype + ': detected') for l in text.splitlines())
    for etype in DEFERRED:
        line = [l for l in text.splitlines() if l.startswith(etype)][0]
        assert 'not implemented' in line and 'deferred_unverified_mapping' in line
        assert 'detected' not in line
