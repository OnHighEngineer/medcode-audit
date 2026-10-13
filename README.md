# medcode-audit

An agent that audits medical codes (ICD-10 first, CPT later) against chart evidence, so billing teams catch coding errors before claims go out and get denied.

Input: a clinical note + the claimed codes. Output: per code a verdict (correct / unsupported / wrong specificity), missed codes, and evidence spans from the chart.

Built in 30 days, spec-driven. See `docs/specs/`, `docs/plans/`, `SESSION.md`, `decision-log.md`, `flow.md`.

## Data policy
All fixtures in git are SYNTHETIC and labelled as such. No Arintra data, no restricted patient text (e.g. MIMIC) is ever committed, logged, screenshotted or demoed. See decision-log.md.

## Working rules
See `AGENTS.md`.
