# Spec 009: LLM auditor v1 (offline-first)

## Contract
Module `medcode_audit.llm_auditor`. No network, no SDK, no credentials: the
model call is an injected `transport(prompt: str) -> str` callable. Tests use
canned replies only.

### Prompt
`build_prompt(note_text, claimed_codes) -> str`
- `note_text` must be a string and `claimed_codes` a list of strings, else
  ValueError. The prompt contains the full note, every claimed code, the four
  verdict names from spec 007, and the requirement that every SUPPORTED verdict
  carries a verbatim `evidence_quote` copied from the note. It asks for one
  JSON object `{'verdicts': [...], 'missed_codes': [...]}` and nothing else.

### Parsing
`parse_model_reply(reply_text) -> dict`
- `reply_text` must be a string, else ValueError. Tolerates ``` fences and
  prose around the JSON object; extracts the first `{` to the last `}`.
  Anything unparseable or not a JSON object: ValueError. Returns the parsed
  dict unvalidated (shape checking is spec 007's job).

### Auditor
`make_llm_auditor(transport) -> auditor` where `auditor(note_text, claimed_codes)`:
1. builds the prompt, 2. calls `transport(prompt)`, 3. parses the reply,
4. validates it with `validate_auditor_output(..., claimed_codes, note_text)`
   (a fabricated quote fails here), 5. returns the validated dict.
- `transport` must be callable, else ValueError. Malformed replies raise
  ValueError (fail closed); transport exceptions propagate unchanged. Inputs
  are never mutated; the same transport reply always yields the same output.

`static_transport(reply)` returns a transport that always answers `reply`
(tests and offline demos).

## Non-goals
Live provider integration, credentials, retries, cost/latency tracking
(item 20), prompt tuning, new verdict names. A live eval needs explicit
approval: provider, secure secret intake, spend cap, data scope. All outputs
stay provisional until the milestone 6 review.
