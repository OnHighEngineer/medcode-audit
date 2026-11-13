# Interview write-up: medcode-audit

What I built, the decisions that matter, and what I rejected. Every claim
here traces to decision-log.md (dates cited) and the specs under
docs/specs/. All counts are provisional: synthetic labels, no clinical
review yet (milestone 6) - they show the harness works, not that a model
is good.

## The project in one paragraph
An offline evaluation harness that audits claimed medical codes against
chart evidence, provider side: catch coding errors before a claim is
denied. Charts are clearly labelled synthetic fixtures - no patient data,
no employer data, nothing that needs an approval. A rule baseline and an
LLM auditor (behind an injected transport, so tests never call a
provider) are scored against gold labels by the same eval runner, and
every run is stamped PROVISIONAL until a human reviews the labels.

## Decisions I would defend in a room

1. Audit, don't assign (2026-10-13). Checking claimed codes is cleaner
   to score - inject a known error, see whether it is caught - and less
   crowded than building another code-assigning agent.
2. Synthetic-first data (2026-10-13). MIMIC is gated (DUA, credentialing,
   no sharing, restricted LLM use) and employer records are off limits.
   Synthetic fixtures need no approval and are safe to publish. MIMIC, if
   ever, is a separate private track that never touches this repo.
3. Fail closed everywhere (2026-10-17, 2026-10-22, 2026-11-12). The
   auditor's output is validated before it is scored: fabricated evidence
   quotes and dropped verdicts raise, malformed model replies raise, and
   the day-30 noisy lanes prove both halves - plausible-but-wrong
   verdicts surface as visible false flags while fabricated or
   incomplete output aborts the eval loudly instead of producing a
   confident wrong number.
4. One verbatim evidence rule (2026-10-14, 2026-10-23). A quote must be
   an exact substring of the note, and gold data and auditor output are
   held to the same standard. If I relaxed it for gold labels, the eval
   would grade the model against unverified truth.
5. Provisional counts until human label review (2026-10-13, milestone
   6). Synthetic labels can be wrong, and bad labels make eval numbers
   meaningless. The repo refuses to call any count a result until a
   sampled label review signs off - automating that judgment is exactly
   the failure mode this project exists to catch.
6. Eval harness before model quality (2026-11-08/09/10/12). Snapshots
   pin behavior across seeds and lanes; a canned gold-truth lane proves
   good replies flow through end to end; noisy lanes prove bad replies
   are caught. The harness had to be trustworthy before any model number
   meant anything.
7. Offline-first LLM work (2026-10-22). The auditor speaks JSON through
   an injected transport. Canned transports stand in for a provider in
   every test: zero spend, zero keys, fully deterministic CI.
8. Test-first with frozen tests (2026-10-13, 2026-10-15). New tests are
   written and run red before implementation, frozen once passing, and
   CI enforces the suite on Python 3.10 and 3.11 on every push. Editing
   a committed test is a logged, exceptional decision, not a habit.

## What I deliberately rejected
- A code-assigning coder agent (crowded, harder to score).
- MIMIC or any real patient data in this repo (DUA, confidentiality).
- pydantic/JSON Schema for a 5-field case schema (stdlib validation
  names the failing field, no dependency).
- A text classifier as the gold oracle (circular evaluation).
- Prose negation detection (out of scope; assertion status comes from
  closed scenario sentences, 2026-10-24).
- LLM-generated fixtures (cost, label drift; 2026-10-15).
- Fuzzy evidence matching (hides label errors).
- Publishing benchmark claims before label review.
- Realistic names/dates in fixtures (unnecessary identifiers).
- A big-bang CPT+ICD scope (ICD first, CPT after the vocabulary
  decision, 2026-10-13).

## Licensing and data posture
ICD-10 codes are validated by shape only in v1; the description lookup
is small, hand-checked, and license-safe (2026-10-26), and upcoding
ranks come from official published titles, ordinal families only
(2026-10-29). No mapping is ever invented without a verified source -
unresolved codes are recorded as deferred, not guessed (visible in the
demo's runner summary). The procedure-code vocabulary for the next
milestone (placeholder vs licensed substitution vs CPT) is an open
decision I am holding until the legal posture is verified, not assumed
from pattern plausibility (2026-11-04).

## Engineering process
Spec-driven: every feature has a spec under docs/specs/, a daily plan
under docs/plans/, and dated decision-log entries recording what was
rejected and why. Fresh session per feature; SESSION.md, decision-log.md
and flow.md rebuild context. 395 tests, green on Python 3.10.12 and
3.11, CI-enforced on every push. 31 days of consecutive commits.

## If I had two more weeks
Finish the label review (milestone 6) so counts can lose the PROVISIONAL
stamp; resolve the procedure vocabulary decision and add the CPT lane;
run the noisy corruptions statistically once they earn it; then the
private MIMIC validation track under its DUA.
