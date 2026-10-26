# Decision Log
Each entry: what I chose, why, what I rejected and why. This is not a change log.

---

### 2026-10-13: What to build
- **Chose:** An auditor that checks claimed codes against chart evidence.
- **Why:** Matches prior medical-coding work at a YC-backed healthcare AI startup; cleaner to test (inject known errors, see if caught).
- **Rejected:** A code-assigning agent (coder) - crowded, harder to score, not the goal.

### 2026-10-13: Whose side
- **Chose:** Provider side (catch errors before claim denial).
- **Why:** Strongest story, fits public/synthetic chart data, demos cleanly.
- **Rejected:** Insurer side first - needs simulated claim queue; same engine so it can be pitched later.

### 2026-10-13: ICD first, CPT later
- **Chose:** ICD-10 in v1, CPT in week 4 using synthetic cases.
- **Why:** Public CPT gold data is scarce.
- **Rejected:** Both at once - doubles scope in 30 days.

### 2026-10-13: Synthetic-first data
- **Chose:** Clearly labelled synthetic charts and codes for the first milestone.
- **Why:** MIMIC is gated (credentialing, training, DUA, ~1-2 week approval, no sharing, external LLM use restricted to zero-retention). Employer records are off limits. Synthetic needs no approval and is safe to publish.
- **Rejected:** MIMIC-first - blocked on access, risk of leaking restricted text. Rejected employer data - confidentiality.

### 2026-10-13: MIMIC as separate private track
- **Chose:** Optional later track, access-verified, kept outside this repo, zero-retention LLM only.
- **Why:** Gives real-world validation without breaking the DUA.
- **Rejected:** Committing any MIMIC text, outputs or screenshots here.

### 2026-10-13: Label validation step
- **Chose:** Manually validate gold labels on a sample before trusting scores (plan item 6).
- **Why:** Synthetic labels can be wrong; bad labels make eval numbers meaningless.
- **Rejected:** Trusting generated labels as-is.

### 2026-10-13: Process rules
- **Chose:** Spec-driven, tests frozen once written, fresh session per feature, daily build-test-push, decision-log + flow updated every change.
- **Why:** Keeps the build honest and the reasoning interview-ready.
- **Rejected:** Editing tests to pass (hides regressions); long shared sessions (context drift).

### 2026-10-13: Language/tooling
- **Chose:** Python + pytest.
- **Why:** His strongest stack, standard for eval work.
- **Rejected:** TypeScript - weaker eval/ML ecosystem for this.

---

### 2026-10-13: Commit authorship
- **Chose:** All commits authored and committed as Manjunath S <manjuss0409@gmail.com>, no co-author trailers.
- **Why:** He owns the project and must be the sole visible contributor.
- **Rejected:** Letting tools or agents add themselves as author or co-author (default behavior of some coding tools).

---

### 2026-10-13: Superpowers-style workflow and docs layout
- **Chose:** brainstorm -> spec -> plan -> TDD per feature, with docs under docs/brainstorms, docs/specs, docs/plans.
- **Why:** Matches how he wants to work; leaves a readable trail of reasoning per feature.
- **Rejected:** Single root spec.md/PLAN.md (does not scale to 30 features); coding first and documenting later.

---

### 2026-10-13: Repo as persistent memory (SESSION.md)
- **Chose:** A written start/end session protocol; every session reads plans, decision-log.md, flow.md first and updates them last.
- **Why:** Fresh-session-per-feature loses context otherwise; the docs rebuild it.
- **Rejected:** Relying on chat history or tool memory (not portable, not reviewable); one long shared session (context drift).


---

### 2026-10-14: Case schema is plain dataclasses and stdlib validation
- **Chose:** Frozen dataclasses plus hand-written validation in `schema.py`, raising one `CaseValidationError`.
- **Why:** No dependency to install, errors name the failing field, and the rules are small enough to read in one screen.
- **Rejected:** pydantic (extra dependency for 5 fields); JSON Schema files (a second language for rules, weaker error messages).

### 2026-10-14: Validate ICD-10 code shape only, no lookup yet
- **Chose:** Regex check (letter, two digits, optional dot, 1-4 alphanumerics) on `gold_codes[].code`.
- **Why:** The license-safe code list is still an open question from the brainstorm, and the code lookup tool is plan item 15.
- **Rejected:** Bundling a code table now (license risk, scope creep); accepting any string (typos would pass silently into gold labels).

### 2026-10-14: Evidence quote must be a verbatim substring of the note
- **Chose:** Case-sensitive exact substring check at load time.
- **Why:** Same rule the evidence verifier will apply to the auditor later, so gold data and auditor output are held to one standard.
- **Rejected:** Fuzzy or whitespace-normalised matching (hides label errors); skipping the check for gold data (bad labels make scores meaningless).

### 2026-10-14: Strict `synthetic: true`
- **Chose:** Reject anything other than the boolean `true`, including missing, false, "true" and 1.
- **Why:** The data policy depends on every fixture being labelled; a loose check would let an unlabelled case in.
- **Rejected:** Truthy check (accepts "false" as a string).

### 2026-10-14: pytest `pythonpath = ["src"]` in pyproject
- **Chose:** Set pythonpath in pytest config so tests import `medcode_audit` without installing the package.
- **Why:** One line, works on any machine, no packaging step needed yet.
- **Rejected:** `pip install -e .` as a prerequisite (needs a build backend section we do not have yet); sys.path edits inside tests.

### 2026-10-14: Commit cadence
- **Chose:** 3-4 heavy days (10+ commits) then 1-2 light days (1-2 commits); light-day work is batched into the next heavy day. Bundle related changes into one meaningful commit.
- **Why:** Matches how Manju wants the history to look and keeps each commit explainable in an interview.
- **Rejected:** Equal commits every day (forces noise commits); one big commit per week (loses the reasoning trail).

### 2026-10-15: Closed templates and local random state
- **Chose:** Five provisional day-1 condition mappings, round-robin coverage, seeded local RNG for neutral wrappers, no identifier fields or free text.
- **Why:** Small batches cover every condition; exact evidence survives every wrapper; output is reproducible without accessing patient records or an API.
- **Rejected:** LLM generation (cost and label drift); random condition selection (can miss conditions); global random.seed (changes caller state); realistic names and dates (unnecessary identifiers).

### 2026-10-15: Generated IDs and API boundaries
- **Chose:** JSON-ready independent dictionaries, gen-* IDs starting at 004, strict integer parameters, pure generation without file writes.
- **Why:** Reuses parse_case, avoids collisions with syn-* fixtures and mutable-record aliasing; the caller controls later batch ranges.
- **Rejected:** Returning dataclasses (needs another serializer); overwriting fixture files inside the API (silent data loss); allowing bool as int (surprising counts).

### 2026-10-15: Positive-only provisional labels
- **Chose:** One explicit positive diagnosis per note; 10 seed-42 fixtures; defer negation, uncertainty and clinical label review to the next plan.
- **Why:** Establishes a small deterministic source before adding harder gold-label rules. Schema validation is not clinical validation.
- **Rejected:** Mixing contradictory negation into gold notes now (ambiguous truth); claiming a validated benchmark before manual review.

### 2026-10-15: Red tests locally, green remote history
- **Chose:** Write and freeze generator tests before implementation; run red locally (missing generator import); publish the passing implementation before the unchanged tests.
- **Why:** Preserves test-first development and the no-failing-push rule at the same time. No existing tests changed.
- **Rejected:** Pushing a red test commit (breaks AGENTS.md); weakening tests after implementation (hides defects).

### 2026-10-15: Web-editor commit metadata
- **Chose:** Continue the signed-in OnHighEngineer web editor with manjuss0409@gmail.com; document its account display-name author and GitHub platform committer exception in AGENTS.md.
- **Why:** Preserves the sole visible project contributor and the established web-editor route. GitHub controls the web commit's platform committer.
- **Rejected:** Claiming web commits have local-git committer metadata (not true); adding co-author trailers or using a different contributor account (violates ownership).

### 2026-10-15: Explicit assertion labels, not a text classifier
- **Chose:** Separate affirmed, negated and uncertain states with closed sentences; only affirmed states enter gold, including in mixed notes. Quote the full affirmed sentence.
- **Why:** Gold truth comes from the scenario, not from the auditor being evaluated. Full-sentence evidence preserves assertion scope. Negative and uncertain notes provide empty-gold controls.
- **Rejected:** Keyword extraction as the gold oracle (circular evaluation); equating uncertainty with negation (different evidence states); claiming these are payer rules (context-dependent and out of scope).

### 2026-10-15: Fixed 37-scenario expansion without new mappings
- **Chose:** A separate pure goldset module, five existing provisional mappings and 37 unique scenarios: single statuses, positive/negative pairs, positive/uncertain pairs, multi-positive and all-nonpositive controls.
- **Why:** Reaches 50 cases while varying support patterns, keeps the frozen day-2 generator reproducible and avoids adding unverified code descriptions.
- **Rejected:** Randomly cloning wrappers to reach a count (little new label coverage); modifying the day-2 generator or fixtures (breaks reproducibility); describing template diversity as real clinical generalization.

### 2026-10-15: Fail closed on repeated conditions
- **Chose:** Reject any repeated condition within a scenario, even when statuses match.
- **Why:** Prevents duplicate gold codes and unresolved contradictory evidence without adding an adjudication policy.
- **Rejected:** Last assertion wins (silently discards contradictory evidence); supporting temporal contradictions today (needs its own spec).

### 2026-10-15: Day-3 verification and review boundary
- **Chose:** Write and freeze new tests before implementation, capture missing-module red locally, publish implementation and fixtures before unchanged tests; retain a provenance/review checklist.
- **Why:** Keeps remote history green, preserves original tests, and separates structural checks from clinical validation. No scores are trusted before milestone 6.
- **Rejected:** Publishing failing test commits; treating generated-label agreement as independent clinical review; weakening tests to suppress a pytest iterator deprecation warning.

### 2026-10-16: Claimed codes live in a separate result, gold stays immutable
- **Chose:** `inject_error(case, error_type, seed)` returns a new dict with `claimed_codes` (origin gold or injected), the injection, and expected findings. The input case and its gold_codes are never touched.
- **Why:** The auditor is scored against gold. Editing gold to carry a claim would erase the truth. No schema change, so the 91 frozen tests stay valid.
- **Rejected:** Mutating gold_codes; adding a claimed field to the frozen Case schema today.

### 2026-10-16: Only three error types implemented; upcoding and wrong_code deferred
- **Chose:** Implement missed_code, unsupported_code and negated_condition. upcoding and wrong_code return `applicable: false` with reason `deferred_unverified_mapping`.
- **Why:** The five code mappings have no verified hierarchy or same-family table, and no license-safe source was checked in. Inventing severity relationships would put unverified clinical claims into the eval labels.
- **Rejected:** Treating a swap of unrelated codes as wrong_code (it is just missed plus unsupported); hand-writing an upcoding ladder.

### 2026-10-16: No RNG, seed picks from a fixed candidate order
- **Chose:** Candidates in table or gold order; index is seed % len(candidates). Seed must be a real int.
- **Why:** Exact reproducible output without touching global random state.
- **Rejected:** random.Random(seed) shuffles (harder to hand-verify in tests).

### 2026-10-16: Explicit inapplicability instead of silent no-ops
- **Chose:** Closed reasons: no_gold_code, no_unmentioned_condition, no_negated_target, deferred_unverified_mapping. Empty-gold controls cannot support missed_code; negated_condition needs the explicit day-3 absent sentence, not merely uncertain or absent text.
- **Why:** Callers and later metrics must tell "not applicable" from "injected nothing".
- **Rejected:** Returning the unchanged claim list; treating uncertain as negated.

### 2026-10-16: Lexical mention check is limited to the closed vocabulary
- **Chose:** unsupported_code targets conditions whose phrase and stem (diabet, hypertens, asthma, kidney, anemi) are absent from the note.
- **Why:** Cheap and exact for the five provisional conditions.
- **Rejected:** Presenting it as NLP mention detection; it does not generalize beyond this vocabulary.

### 2026-10-16: Two tests of my own corrected before first commit
- **Chose:** Two assertions compared whole results including the seed field, and one expected count (negated applicable) was miscounted as 20; fixed to compare claimed_codes/injection and 16 (5 negated singles + 10 affirmed/negated pairs + 1 all-negated). Counts derived from the scenario schedule.
- **Why:** The spec was right; the draft tests were wrong before ever being published. No committed test changed.
- **Rejected:** Changing the implementation to match a miscounted test.

### 2026-10-17: Auditor is a plain callable that sees only note and claimed codes
- **Chose:** `auditor(note_text, claimed_codes) -> {'verdicts': [...], 'missed_codes': [...]}`. The runner never passes origins, injection or expected findings.
- **Why:** A stub or later auditor cannot pass by reading the answer. Real auditors plug in without runner changes.
- **Rejected:** Passing the whole injected result (leaks truth); building a concrete rule auditor inside the runner (week 2 work).

### 2026-10-17: Output validation fails closed
- **Chose:** Verdicts must cover exactly the claimed codes once each, use known verdict names, and `missed_codes` must be a list of strings. Anything else raises ValueError.
- **Why:** A malformed auditor reply must not be counted as a miss or a hit.
- **Rejected:** Treating malformed output as "not detected" (hides auditor bugs inside the metrics).

### 2026-10-17: How expected findings are matched
- **Chose:** missed is detected when the removed code is in `missed_codes`. unsupported and negated_claim are detected when the injected code gets UNSUPPORTED. WRONG_SPECIFICITY is an accepted verdict but no implemented error type expects it.
- **Why:** A negated condition has no support in the note, so UNSUPPORTED is the only verdict that fits without a new policy.
- **Rejected:** A separate NEGATED verdict (changes spec 000 for one case); counting WRONG_SPECIFICITY as detection.

### 2026-10-17: Report prints counts, flags false positives, and hides deferred types
- **Chose:** Plain text, first line says provisional, counts as `detected k/n`, no percentages. `false_flags` counts gold-origin claims the auditor did not mark SUPPORTED. upcoding and wrong_code print "not implemented" with the injector reason and no counts.
- **Why:** Scores are not trusted before milestone 6, and a deferred type must not look covered. Detection alone rewards an auditor that flags everything, so false flags sit beside it.
- **Rejected:** Percentages or an overall score; silently omitting deferred types; a CLI today.

### 2026-10-17: Test-first order and a runner draft written early
- **Chose:** Spec and tests were written first. The runner draft was written before the red run was captured; red was then confirmed by removing the module (collection error), restoring it, and running the full suite unchanged.
- **Why:** Records what happened so the sequence is not overstated. No committed test changed.
- **Rejected:** Claiming a clean red-then-green sequence that did not occur.

### 2026-10-18: Strata come from the closed assertion sentences
- **Chose:** `stratum_key` reads the note for the three spec-003 markers and returns presence letters in fixed order (`A`, `N`, `U`, combinations, or `none` for prose notes).
- **Why:** The markers are part of the frozen day-3 spec, so strata are inspectable and stable, and the day-1/2 prose cases still get sampled via `none`.
- **Rejected:** Adding status fields to the schema (a schema change with its own spec); sampling by file name or batch (couples review to directory layout).

### 2026-10-18: Round-robin stratified sampling with seeded rotation
- **Chose:** Group by stratum, order strata by key, sort each stratum by id, rotate by `seed % len`, then take round-robin across strata until the requested size.
- **Why:** Every support pattern in the set is guaranteed a seat, the rule is hand-verifiable, and the seed changes the sample without RNG state.
- **Rejected:** `random.Random(seed)` shuffle (harder to hand-verify); first-N (skips whole label patterns); proportional allocation (tiny strata could get zero seats).

### 2026-10-18: One sheet row per gold label, control row for empty gold
- **Chose:** One row per (case, gold code) with `reviewer_mark` (`agree`/`disagree`/null) and `reviewer_note`; an empty-gold case gets one row with null code and quote so the reviewer confirms nothing is supported.
- **Why:** Each label is judged on its own, and an empty gold list is itself a label that can be wrong.
- **Rejected:** One row per case with a code list (cannot mark codes independently); CSV (lossy round trips, weaker validation).

### 2026-10-18: Counts-only agreement summary; disagreements fixed only by logged decision
- **Chose:** `summarize_review` returns total/reviewed/unreviewed/agree/disagree counts plus the disagreement rows. Disagreements stay in the sheet; a fixture changes only through a decision-log entry.
- **Why:** Counts are the auditable artifact; the sheet is the evidence and the log is the authority, so label history stays traceable.
- **Rejected:** Percentages or kappa in the summary (small set, implies more certainty than a 12-case sample holds); editing fixtures directly from review notes.

### 2026-10-18: Sample artifact is 12 cases, seed 42, checked into docs/reviews
- **Chose:** `docs/reviews/day-06-label-review-sheet.json` holds the unmarked sheet for `sample_cases(all 50 cases, 12, seed=42)` - two cases from each of the six strata, 12 rows.
- **Why:** Gives the milestone 6 human review a concrete, reproducible starting sheet without claiming any review happened.
- **Rejected:** Sampling all 50 (defeats the purpose of a sample); not checking the sheet in (the reviewer would have to regenerate it).

### 2026-10-18: Green push order on a heavy day
- **Chose:** Tests were written and frozen first and ran red locally (missing module); commits publish the implementation before the new tests so every pushed state is green, as on days 2-3. Suite: 142 passing on Python 3.10 (3.11 still unavailable in the sandbox).
- **Why:** Keeps test-first development and the never-push-failing rule at once.
- **Rejected:** Pushing the red test commit first (breaks AGENTS.md); one squashed commit (loses the heavy-day trail).

### 2026-10-19: Python 3.11 rerun closes the version caveat
- **Chose:** Ran the full suite on Python 3.11.16 (installed via uv in the sandbox) alongside 3.10.12: 142 passing on both. Recorded both versions in the week-1 review and SESSION.md.
- **Why:** The project targets 3.11 and days 5-6 could only verify 3.10; the open question is now closed with evidence.
- **Rejected:** Leaving the 3.10-only caveat standing (it implied unverified risk that no longer exists).

### 2026-10-19: Label review guide lives in docs/reviews; gate stays visible
- **Chose:** A short reviewer-facing guide (`docs/reviews/label-review-guide.md`) next to the sample sheet, and a week-1 review note that re-checks the provisional gate in README, flow.md, SESSION.md and the runner report.
- **Why:** The milestone 6 review is pending with a human; the guide makes it executable without inventing any clinical judgment, and the gate check proves no score reads as trusted.
- **Rejected:** Putting review instructions only in chat (not durable, not versioned); automating any part of the judgment (out of scope by spec 006).

### 2026-10-19: Week-1 consistency read found no drift
- **Chose:** Read decision-log.md against flow.md and specs 001-006; every flow layer traces to a spec and decision entries; deferred items match across all three. No corrections needed.
- **Why:** Week 2 builds on these documents; a quiet drift would surface as rework mid-week.
- **Rejected:** Skipping the read because the same author wrote everything (fresh eyes per session is the protocol).

### 2026-10-20: Auditor output contract becomes a module; runner re-exports VERDICTS
- **Chose:** `medcode_audit/auditor_schema.py` owns `VERDICTS` and `validate_auditor_output`; the runner imports and re-exports `VERDICTS` so frozen day-5 imports keep working.
- **Why:** Week-2 auditors need an importable, separately tested contract instead of the runner's inline checks.
- **Rejected:** Keeping validation inline in the runner (unimportable, drifts per auditor); moving the name without a re-export (breaks frozen tests).

### 2026-10-20: Evidence quote is optional but verbatim-checked when volunteered
- **Chose:** A verdict may carry `evidence_quote`; it must be a nonempty string and, when the caller passes the note, a verbatim case-sensitive substring. The runner passes the note, so volunteered quotes are checked against the chart from today.
- **Why:** The LLM auditor (item 10) must return quotes; holding them to the gold-evidence standard now gives item 11 its hook without writing verification policy yet. No committed auditor returns quotes, so no current behavior changes.
- **Rejected:** Requiring quotes on every verdict (a missed code has no span; item 11 owns that policy); accepting quotes unchecked (lets auditors fabricate support).

### 2026-10-20: Validator returns a normalized deep copy
- **Chose:** `validate_auditor_output` returns a fresh dict (verdicts cleaned to known keys, missed_codes copied) and never mutates the auditor's reply.
- **Why:** Callers can annotate results without aliasing auditor state; the copy is proof the shape passed.
- **Rejected:** Returning the input object (aliases mutable auditor state); returning only an error-or-None (every caller rebuilds the same maps).

### 2026-10-21: Baseline knows only the five mappings and the closed sentences
- **Chose:** `audit_baseline` scores with the five provisional (code, phrase, stem) mappings plus the spec-003 assertion sentences, in priority affirmed > negated > uncertain > mention > absent. SUPPORTED only for affirmed or plain mention; unknown claimed codes are UNSUPPORTED.
- **Why:** The baseline is the honest floor for the LLM auditor: exactly what the data was built from, nothing more. Its perfect goldset detection is recorded as expected, not as a result.
- **Rejected:** General negation or keyword NLP (unverifiable on this vocabulary, hides the limits); treating unknown codes as SUPPORTED-by-default (would fabricate support).

### 2026-10-21: Baseline volunteers verbatim evidence quotes
- **Chose:** SUPPORTED verdicts quote the affirmed sentence or the verbatim matched prose substring; negated UNSUPPORTED verdicts quote the absent sentence; uncertain/absent verdicts carry no quote.
- **Why:** Exercises the day-8 verbatim check on a real auditor and makes every verdict inspectable; all quotes are verbatim by construction.
- **Rejected:** No quotes (wastes the spec-007 hook); paraphrased quotes (would fail the verbatim check the runner enforces).

### 2026-10-21: The baseline duplicates the mapping table
- **Chose:** baseline.py carries its own copy of the five (code, phrase, stem) mappings, intentionally isolated like the goldset's copy.
- **Why:** Sharing a private table across generator, injector, goldset and baseline couples independently evolving modules; the mappings are provisional and small.
- **Rejected:** Importing the injector's private `_TABLE` (couples modules); a shared constants module today (premature for five rows).

### 2026-10-21: Baseline counts published as a provisional floor
- **Chose:** Recorded the full-50-case run in docs/reviews/day-09-baseline-eval.md with the runner's provisional report and an explicit "expected, not a result" caveat.
- **Why:** Week-2 comparisons need a recorded baseline, but 100% detection on self-templated data must not read as a solved problem.
- **Rejected:** Publishing counts without the caveat; withholding them until milestone 6 (the floor is useful precisely because it is recorded early).

### 2026-10-22: LLM auditor is offline-first with an injected transport
- **Chose:** `make_llm_auditor(transport)` takes a `transport(prompt) -> reply_text` callable; the module has no network, SDK or credential handling, and tests run on canned replies via `static_transport`.
- **Why:** The suite stays offline and deterministic; a live provider call is a later, separately approved step (provider, secure secret intake, spend cap, data scope), not something the module can stumble into.
- **Rejected:** Direct SDK calls in the module (network in the unit path, credentials near code); a config-file key route (secrets do not belong in git or chat).

### 2026-10-22: Prompt shows the note and claimed codes only
- **Chose:** The v1 prompt contains the full note, the claimed codes as JSON, the four verdict names, and the requirement that SUPPORTED verdicts carry a verbatim evidence_quote. It does not include the baseline's five-phrase table.
- **Why:** The model must read the chart; handing it the toy vocabulary would cap what v1 can demonstrate and leak the test fixture's structure.
- **Rejected:** Constraining the prompt to the five known phrases (revisit only if a later eval needs constrained decoding).

### 2026-10-22: Malformed model replies fail closed
- **Chose:** `parse_model_reply` tolerates fences and surrounding prose but raises ValueError on anything unparseable or non-object; the auditor then validates through spec 007 with the note, so fabricated quotes also raise. Transport exceptions propagate unchanged.
- **Why:** A crashed run is honest; a silently miscounted one corrupts the eval. The runner's fail-closed stance now extends across the model boundary.
- **Rejected:** Counting malformed replies as "not detected" (hides model/parser bugs in the metrics); retrying inside v1 (masks instability; a live transport can add retries later).

### 2026-10-22: No cost or latency tracking in v1
- **Chose:** The module records nothing about calls; the transport boundary is where a future live integration times and prices them (plan item 20).
- **Why:** Keeping the module pure lets the tracking hook wrap any transport without changes here.
- **Rejected:** Timing inside the auditor (mixes concerns, complicates offline tests).

### 2026-10-23: SUPPORTED without a quote is flagged, not failed
- **Chose:** The verifier reports `unverified` for a SUPPORTED verdict with no evidence quote; only non-verbatim quotes are hard failures (at the spec-007 boundary, as since day 8).
- **Why:** Frozen day-5/8 tests run stub auditors that return SUPPORTED without quotes, and frozen tests do not change. A visible flag keeps the accounting honest without rewriting history.
- **Rejected:** Hard-failing quote-less SUPPORTED in the runner (breaks frozen tests); ignoring missing quotes entirely (silently accepts unverifiable support).

### 2026-10-23: One verbatim rule, one implementation
- **Chose:** `evidence.find_span` owns the case-sensitive substring check and returns (start, end) offsets; `auditor_schema` imports it for validation, and the verifier reuses it for spans. The verifier reads the verdict vocabulary lazily from the schema module to keep the import one-directional.
- **Why:** A single source of truth for the rule gold data and auditors are held to; spans come free for the item-22 report generator.
- **Rejected:** Duplicating the substring check in both modules (drift); moving VERDICTS into the evidence module (verdicts are not evidence); changing the runner's record shape (frozen tests).

### 2026-10-23: Verification statuses are a closed four-value set
- **Chose:** `verified`, `unverified`, `invalid`, `not_applicable`; non-SUPPORTED verdicts may carry quotes (checked like any other) and are `not_applicable` without one.
- **Why:** Closed vocabularies have kept every layer testable so far; summaries zero-fill all four keys.
- **Rejected:** Per-verdict-type status sets (harder to count); a boolean verified flag (cannot express "flagged, not failed").

### 2026-10-24: Assertion detection has six closed statuses, including conflict
- **Chose:** `affirmed`, `negated`, `uncertain` (closed spec-003 sentences), `mentioned` (lexical prose match), `absent`, and `conflict` for contradictory closed sentences, which lists every matched sentence.
- **Why:** Prose mentions are weaker than affirmed sentences and must not read as equal; a contradiction must surface, not resolve silently - the same failure the day-3 goldset rejected with duplicate conditions.
- **Rejected:** Priority rules that pick a winner (discards contradictory evidence); collapsing mentioned into affirmed (hides the difference).

### 2026-10-24: No prose negation detection
- **Chose:** Prose matches are `mentioned`; the detector does not guess negation or uncertainty in free text. The day-1/2 prose fixtures are positive-only by construction, so nothing in the repo depends on prose negation.
- **Why:** General negation detection is NLP the project has refused since day 3; claiming it here would be unverifiable on this vocabulary.
- **Rejected:** Keyword negation heuristics over prose (exactly the unverifiable NLP rejected repeatedly); treating uncertain prose hints as negated (different evidence states).

### 2026-10-24: Baseline consults the shared detector; conflicts are UNSUPPORTED
- **Chose:** The baseline dropped its private state logic and maps `detect_assertions` records (affirmed/mentioned SUPPORTED with quote, negated UNSUPPORTED with the absent sentence, conflict/uncertain/absent UNSUPPORTED without one). Fixture behavior is identical.
- **Why:** One detector, one policy, for every current and future auditor; a conflict must not fabricate support.
- **Rejected:** Keeping two assertion readers (drift); quoting the affirmed sentence on a conflict (there is no single truth to quote).

### 2026-10-25: Comparison uses two canned LLM personas, not one
- **Chose:** The day-13 comparison records the baseline beside a canned perfect-reader transport AND a canned flag-everything transport, all offline.
- **Why:** Perfect vs baseline shows the ceiling; flag-all shows the eval is not gamed by detection counts (48/48 "detected" beside 45 false flags). One persona would have shown only half the story.
- **Rejected:** A single perfect canned persona (cannot demonstrate the false-flag guard); any live model call (not approved; offline-first stands).

### 2026-10-25: Day 13 adds no library code
- **Chose:** The comparison is a review note with an inline reproduction snippet over existing public APIs; no new module, no test changes.
- **Why:** A light day; the eval surface was already complete, and new code would exist only to be run once.
- **Rejected:** A scripts/compare.py checked in (premature; the note's snippet reproduces exactly).

### 2026-10-26: Week-2 consistency read found no drift
- **Chose:** Read decision-log.md against flow.md and specs 007-011; every flow layer traces to a spec and decision entries, and the deferred items (live LLM run, upcoding/wrong_code, milestone 6 review) match across all three. No corrections needed.
- **Why:** Week 3 adds an agent loop and tools on top of these documents; quiet drift would surface as rework mid-week.
- **Rejected:** Skipping the read because the same author wrote everything (fresh eyes per session is the protocol).

### 2026-10-26: Day 14 adds no library code
- **Chose:** The week-2 review is a review note (docs/reviews/day-14-week-2-review.md) plus closeout updates; no module or test changes.
- **Why:** A light review day; the only findings are risks for week 3, which belong in the day-15 plan, not in code.
- **Rejected:** Pre-building the day-15 lookup table today (item 15 deserves its own spec-first session).
