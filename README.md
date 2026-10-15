# medcode-audit

An agent that audits medical codes (ICD-10 first, CPT later) against chart evidence, so billing teams catch coding errors before claims go out and get denied.

Input: a clinical note + the claimed codes. Output: per code a verdict (correct / unsupported / wrong specificity), missed codes, and evidence spans from the chart.

Built in 30 days, spec-driven. See `docs/specs/`, `docs/plans/`, `SESSION.md`, `decision-log.md`, `flow.md`.

## Data policy
All fixtures in git are SYNTHETIC and labelled as such. No Arintra data, no restricted patient text (e.g. MIMIC) is ever committed, logged, screenshotted or demoed. See decision-log.md.

## Working rules
See `AGENTS.md`.

## Run the tests
Requires Python 3.11+. Install pytest, then run `python -m pytest -q`.

## Generate synthetic cases (day 2)
From the repository root:
```python
# Run with PYTHONPATH=src, or in an environment with src on the import path.
from medcode_audit.generator import generate_cases
from medcode_audit.schema import parse_case, load_cases

cases = generate_cases(10, seed=42, start_id=4)
validated = [parse_case(case) for case in cases]
fixtures = load_cases('data/synthetic')  # 13 checked-in cases
```
The pure API does not write files. Five consecutive cases cover the five provisional
condition mappings. Seed affects wording only. The notes are deliberately simple;
clinical label review, error injection and auditor evaluation are later milestones.
No accuracy claim is made from this synthetic batch.
