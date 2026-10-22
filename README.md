# medcode-audit

An agent that audits medical codes (ICD-10 first, CPT later) against chart evidence, so billing teams catch coding errors before claims go out and get denied.

Input: a clinical note + the claimed codes. Output: per code a verdict (correct / unsupported / wrong specificity), missed codes, and evidence spans from the chart.

Built in 30 days, spec-driven. See `docs/specs/`, `docs/plans/`, `SESSION.md`, `decision-log.md`, `flow.md`.

## Data policy
All fixtures in git are SYNTHETIC and labelled as such. No real data, no restricted patient text (e.g. MIMIC) is ever committed, logged, screenshotted or demoed. See decision-log.md.

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
fixtures = load_cases('data/synthetic')  # 50 checked-in cases after day 3
```
The pure API does not write files. Five consecutive cases cover the five provisional
condition mappings. Seed affects wording only. The notes are deliberately simple;
clinical label review, error injection and auditor evaluation are later milestones.
No accuracy claim is made from this synthetic batch.

## Assertion scenarios (day 3)

```python
from medcode_audit.goldset import build_gold_cases, make_assertion_case

batch = build_gold_cases()  # 37 deterministic cases, gen-014..050
mixed = make_assertion_case('example', [
    ('E11.9', 'affirmed'), ('I10', 'negated'), ('D50.9', 'uncertain'),
])
assert [item['code'] for item in mixed['gold_codes']] == ['E11.9']
```

There are now 50 checked-in synthetic cases. Negation and uncertainty are separate
explicit states, not inferred by NLP. Only confirmed assertions enter gold; their
full sentences are the evidence. Duplicate conditions are rejected. The batch
covers mixed notes, multiple confirmed conditions and empty-gold controls.
Mappings and labels remain provisional; this is not clinical/payer guidance or an
accuracy benchmark. See spec 003 and `docs/reviews/day-03-provenance.md`.

## Auditors (week 2)

Two auditors plug into the eval runner behind one contract (spec 007):

```python
from medcode_audit.baseline import audit_baseline          # rule baseline (day 9)
from medcode_audit.llm_auditor import make_llm_auditor, static_transport
from medcode_audit.runner import run_eval

run_eval(cases, audit_baseline)                  # lexical, five known conditions
llm = make_llm_auditor(static_transport(canned)) # offline: canned replies only
run_eval(cases, llm)
```

The LLM auditor (day 10) is offline-first: the model call is an injected
`transport(prompt) -> reply` callable. There is no live provider integration,
no credential in this repo, and no network in the tests. A live eval would need
an approved provider, secure secret intake, a spend cap and a data scope first.
Every auditor reply is validated fail-closed, and any volunteered evidence
quote must be a verbatim note substring. All counts stay provisional until the
milestone 6 label review is recorded.
