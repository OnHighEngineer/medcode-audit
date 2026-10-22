# Day 10 brainstorm: LLM auditor v1 (offline-first)

## Problem
The baseline proves the eval loop works on rules. The next auditor is an LLM:
one prompt, per-claim verdicts, evidence quotes required. Two things must be
true before any model is involved: the output contract stays exactly spec 007
(so the runner, metrics and later auditors do not change), and the suite never
touches a network or a credential (offline-first, per the day-10 scope note).

## Options considered

### Where the model call lives
1. A `transport` callable injected into `make_llm_auditor`. Chosen: the auditor
   is `transport(prompt) -> reply_text`; tests inject canned replies, a live
   transport is a later, separately approved step.
2. Direct SDK calls inside the module. Rejected: network in the unit path,
   credentials near code, untestable offline.

### What the prompt shows
1. The note and the claimed codes only. Chosen: the model must read the chart;
   handing it the baseline's five-phrase table would leak the toy vocabulary
   and cap what v1 can demonstrate.
2. Note plus the five known phrases. Rejected for v1 (see above); revisit if a
   later eval needs constrained decoding.

### Malformed replies
Fail closed: any unparsable reply, non-JSON content, or spec-007 violation
(including a fabricated evidence quote, which the runner already rejects)
raises ValueError. A crashed run is honest; a silently miscounted one is not.
Transport exceptions propagate unchanged.

### Cost/latency hooks
v1 records nothing itself: the transport boundary is where a live integration
times and prices calls (item 20 owns tracking). The module stays pure so the
hook can wrap any transport without code changes here.

## Risks
A real model will occasionally return prose around JSON; the parser accepts a
JSON object anywhere in the reply (fences tolerated) and rejects everything
else. All eval outputs stay provisional until the milestone 6 review.
