# Day 13: baseline vs LLM auditor (provisional, offline)

Comparison over all 50 checked-in cases, seed 0, all five error types. Three
auditors, all deterministic and offline:
- `baseline`: the rule auditor (spec 008).
- `llm-perfect`: the spec-009 LLM auditor with a CANNED perfect-reader
  transport. Not a live model; it shows what a perfect reply scores.
- `llm-flag-all`: a canned transport that marks every claimed code UNSUPPORTED
  and reports no missed codes. It shows the eval is not gamed by detection
  counts alone.

## Results

baseline:
```
unsupported_code: detected 48/48, false flags on gold claims 0
missed_code: detected 38/38, false flags on gold claims 0
negated_condition: detected 16/16, false flags on gold claims 0
```

llm-perfect (canned): identical to baseline on every line.

llm-flag-all (canned):
```
unsupported_code: detected 48/48, false flags on gold claims 45
missed_code: detected 0/38, false flags on gold claims 7
negated_condition: detected 16/16, false flags on gold claims 10
```

## What this shows
- Detection alone is gameable: flag-all "detects" every unsupported and
  negated injection while missing every missed code and flagging 62 gold
  claims in total. The false-flag column is what exposes it - this is why the
  runner prints the two side by side.
- Baseline and the perfect canned reader tie: expected on self-templated data,
  not evidence a real LLM matches the baseline. No live model claim is made.
- upcoding and wrong_code remain not implemented (deferred, no verified
  mapping) and print no counts.

## Reproduce
```python
import json, sys
from pathlib import Path
sys.path.insert(0, 'src')
from medcode_audit.runner import run_eval, format_report
from medcode_audit.baseline import audit_baseline
from medcode_audit.llm_auditor import make_llm_auditor

cases = [json.loads(p.read_text())
         for p in sorted(Path('data/synthetic').glob('*.json'))]
by_note = {c['note_text']: c for c in cases}

def perfect_reader(prompt):
    note = prompt.split('NOTE:\n"""\n', 1)[1].split('\n"""', 1)[0]
    claimed = json.loads(prompt.split('CLAIMED_CODES_JSON:\n', 1)[1].split('\n', 1)[0])
    gold = {g['code']: g['evidence_quote'] for g in by_note[note]['gold_codes']}
    verdicts = [{'code': c, 'verdict': 'SUPPORTED', 'evidence_quote': gold[c]}
                if c in gold else {'code': c, 'verdict': 'UNSUPPORTED'}
                for c in claimed]
    return json.dumps({'verdicts': verdicts,
                       'missed_codes': sorted(set(gold) - set(claimed))})

def flag_everything(prompt):
    claimed = json.loads(prompt.split('CLAIMED_CODES_JSON:\n', 1)[1].split('\n', 1)[0])
    return json.dumps({'verdicts': [{'code': c, 'verdict': 'UNSUPPORTED'} for c in claimed],
                       'missed_codes': []})

for auditor in (audit_baseline, make_llm_auditor(perfect_reader),
                make_llm_auditor(flag_everything)):
    print(format_report(run_eval(cases, auditor)))
```

All counts stay provisional: synthetic self-templated labels, milestone 6 human
review still pending. A live LLM run needs explicit approval (provider, secure
secret intake, spend cap, data scope) before it happens.
