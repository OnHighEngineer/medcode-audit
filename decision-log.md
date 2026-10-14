# Decision Log
Each entry: what I chose, why, what I rejected and why. This is not a change log.

---

### 2026-10-13: What to build
- **Chose:** An auditor that checks claimed codes against chart evidence.
- **Why:** Matches Arintra experience; cleaner to test (inject known errors, see if caught).
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
- **Why:** MIMIC is gated (credentialing, training, DUA, ~1-2 week approval, no sharing, external LLM use restricted to zero-retention). Arintra records are off limits. Synthetic needs no approval and is safe to publish.
- **Rejected:** MIMIC-first - blocked on access, risk of leaking restricted text. Rejected Arintra data - confidentiality.

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
