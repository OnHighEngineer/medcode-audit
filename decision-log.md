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
