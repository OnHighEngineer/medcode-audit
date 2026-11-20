# Spec 034: self-check lanes for the committed demo artifacts

## Purpose
The spec-032 self-check guards the data snapshots, but the two
committed demo renderings - docs/reviews/day-27-demo-output.md and
docs/reviews/day-29-demo-report.html - had no guard at all. Spec 027
changed the HTML rendering on Nov 13 (viewport meta, narrow wrapping)
and the day-29 artifact stayed stale for a week, invisible to every
test. This spec pins both artifacts as self-check lanes so doc drift
fails loudly. The day-29 artifact is regenerated to the current
rendering as part of this change (the drift was the intentional
spec-027 change; the artifact, not the renderer, was stale).

## Rules
1. SELF_CHECK_LANES gains two lanes, appended after the snapshot lanes:
   demo_report, demo_html.
2. check_committed_snapshots compares run_demo() against the committed
   day-27 artifact and run_demo_html() against the day-29 artifact,
   byte-exact. The reviews directory is the repo's own docs/reviews
   (resolved from this file's location) unless the reviews_dir
   parameter overrides it; data_dir keeps its spec-032 meaning and does
   not move the artifacts. A missing artifact file raises ValueError.
3. Drift strings name the artifact file and the first differing line
   (expected vs live) plus any line-count mismatch. Lane line format
   and exit 0/1 are unchanged.
4. Import direction stays one-way: regression.py imports the demo
   functions lazily inside check_committed_snapshots, because demo.py
   already imports from regression.

## Non-goals
Pinning the prose review artifacts (they quote numbers; they are not
byte-comparable renderings); updating artifacts from the command
(regenerate by hand and commit, like day 29 did); changing the demo
outputs themselves.
