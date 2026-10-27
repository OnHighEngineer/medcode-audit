# Spec 013: agent loop with tools

Plan item 16. An offline-first loop where the model audits a note across
several turns, calling deterministic local tools between turns. The only
model boundary is the spec-009 style injected transport; every tool is a
pure local function. No network, no credentials, no live call.

## Protocol
The loop keeps a transcript (built deterministically as one string) and asks
the transport for one reply per turn. Each reply must parse as ONE JSON
object (spec-009 fence/prose tolerance) in exactly one of two shapes:
- Tool call: `{"tool": <name>, "args": {...}}` - the tool runs, its JSON
  result is appended to the transcript, and the loop continues.
- Final answer: `{"final": {"verdicts": [...], "missed_codes": [...]}}` -
  validated through spec 007 with the note (fabricated quotes raise), then
  returned normalized. The loop stops.

## Tools (closed set, local and deterministic)
- `lookup_code` `{"code": str}` -> spec-012 lookup; result
  `{"ok": true, "result": <entry>}` or `{"ok": false, "error": <message>}`
  when the code is unknown or malformed (tool errors are observable; the
  model may recover).
- `verify_quote` `{"code": str, "quote": str}` -> spec-010 verbatim check of
  the quote against the note; result `{"ok": true, "result": {"status",
  "span"}}` (`verified` with span offsets, or `invalid`).
- `detect_assertions` `{}` -> spec-011 detector over the note; result
  `{"ok": true, "result": [<assertion records>]}`.

## Fail closed
- Reply that is not one JSON object, has neither `tool` nor `final`, names an
  unknown tool, or carries non-dict args: `ValueError`.
- Tool ARGUMENTS with the wrong types: `ValueError` (protocol violation),
  distinct from a tool-level error result (bad code value).
- `max_steps` tool turns without a final answer: `RuntimeError`. The loop
  never degrades to a partial score.
- Transport exceptions propagate unchanged.
- The final answer goes through spec-007 validation with the note: missing
  claimed codes, unknown verdicts or fabricated quotes raise `ValueError`.

## API (medcode_audit/agent_loop.py)
- `run_agent_audit(note_text, claimed_codes, transport, max_steps=8) -> dict`:
  the validated final answer.
- `make_agent_auditor(transport, max_steps=8)`: wraps the loop as a
  spec-005 auditor callable for `run_eval`.
- `MAX_STEPS = 8`: small and deterministic; a real audit of one note needs
  at most a handful of lookups.
- Type checks on note_text (str) and claimed_codes (list of str) match
  spec 009.

## Decisions
- Tools compose spec-010/011/012 directly as local functions; the model
  boundary stays the transport. The baseline detector is a tool the model
  may consult, not a hidden oracle: every tool call is visible in the
  transcript.
- One JSON object per turn keeps parsing identical to spec 009.
