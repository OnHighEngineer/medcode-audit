# Day 3 provenance and review checklist

## Origin and reproduction
All 37 new notes are closed-template synthetic text. No clinical source, patient
record, employer data, MIMIC data, LLM/API output or identifier is used. Code/phrase
mappings are the same provisional five from day 2, not verified against an official
release. The old 13 fixtures are unchanged.

Reproduce from repo root with PYTHONPATH=src:

```python
import json
from pathlib import Path
from medcode_audit.goldset import build_gold_cases
from medcode_audit.schema import load_cases
for case in build_gold_cases(start_id=14):
    path = Path('data/synthetic') / (case['id'] + '.json')
    # Review before replacing any checked-in fixture.
    assert json.loads(path.read_text()) == case
assert len(load_cases('data/synthetic')) == 50
```

## Batch manifest
| IDs | Scenario | Cases | Gold per case |
| --- | --- | ---: | ---: |
| gen-014..018 | single affirmed | 5 | 1 |
| gen-019..023 | single negated | 5 | 0 |
| gen-024..028 | single uncertain | 5 | 0 |
| gen-029..033 | affirmed + next condition negated | 5 | 1 |
| gen-034..038 | affirmed + second-next condition negated | 5 | 1 |
| gen-039..043 | affirmed + next condition uncertain | 5 | 1 |
| gen-044..048 | two affirmed conditions | 5 | 2 |
| gen-049 | all five negated | 1 | 0 |
| gen-050 | all five uncertain | 1 | 0 |

The five-condition order is E11.9, I10, J45.30, N18.31, D50.9, wrapping at the end.
These cases test assertion scope, not broad linguistic or clinical diversity.
They are not a suitable unseen holdout against a model trained on these templates.

## Automated checks completed during the build
- [x] Exactly 50 unique case IDs in the combined loader.
- [x] 37 distinct new note texts, all schema-compatible.
- [x] Full-sentence evidence appears verbatim; only affirmed conditions in gold.
- [x] Negated and uncertain controls include empty gold lists.
- [x] Fixed batch reproduces the stored JSON; old fixtures/tests unchanged.

## Independent review still pending (milestone 6)
- [ ] Select an official, license-safe ICD-10-CM release and check all five mappings.
- [ ] Review samples from every manifest row, including gen-049 and gen-050.
- [ ] Record reviewer, release, expected labels, disagreements and rationale.
- [ ] Check evidence scope and reject unsupported specificity assumptions.
- [ ] Correct labels transparently if needed; never silently revise frozen tests.
- [ ] Only then decide whether any evaluation scores can be trusted.

No independent clinical review or accuracy claim is recorded today.
