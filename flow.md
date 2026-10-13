# Flow

## System flow (v1 target)
note + claimed codes -> parse/normalize -> auditor (rules baseline | LLM agent) -> per-code verdicts + evidence spans -> evidence verifier (quote must exist in note) -> report

## Eval flow
synthetic gold cases -> error injector -> auditor -> compare verdicts to injected-error truth -> metrics per error type -> report

## Change log of flow
- Setup: initial flow defined.
