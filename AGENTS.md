# Rules for every session (human or agent)

1. Spec-driven: update `docs/specs/` for the feature BEFORE writing code.
2. Write tests first. Once a test is committed, it must NOT be changed to make code pass. Fix the code. A test may change only if the spec was wrong, and that needs its own decision-log entry.
3. Build, test, push every day. Never push with failing tests.
4. One feature per fresh session/chat. Start by reading SESSION.md protocol (docs, plans, decision-log.md, flow.md).
5. Every feature or code change adds an entry to `decision-log.md` (Chose / Why / Rejected) and updates `flow.md`.
6. Synthetic data only in git. No Arintra or restricted patient data anywhere.
7. Authorship: every commit is authored and committed as Manjunath S <manjuss0409@gmail.com> only. No Co-authored-by trailers, no bot or agent names in author, committer or commit messages. Before the first commit in any session run:
   git config user.name "Manjunath S"
   git config user.email "manjuss0409@gmail.com"
   Check with `git log -1 --format='%an <%ae> | %cn <%ce>'` before pushing.
   Enable the guard once: git config core.hooksPath .githooks

## Workflow per feature (Superpowers style)
brainstorm (docs/brainstorms/) -> spec (docs/specs/NNN-name.md) -> plan (docs/plans/) -> failing tests -> implement -> verify -> decision-log.md + flow.md -> commit and push.

## GitHub web editor metadata
Web-UI commits use the signed-in OnHighEngineer account and its selected email
manjuss0409@gmail.com. GitHub records the account display name (currently manjunath)
as author and GitHub <noreply@github.com> as the platform committer. That platform
metadata is an exception to the literal local-git name/committer check above;
it does not add a second project contributor. Never add co-author trailers.
Local-git commits still use the exact Manjunath S identity required above.
