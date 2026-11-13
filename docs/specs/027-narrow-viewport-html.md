# Spec 027: narrow-viewport HTML report polish

The spec-025 renderer is desktop-clean: fenced blocks use
`overflow-x:auto`, so long lines scroll horizontally. On a phone-width
screen that makes the failure-analysis section awkward to read. This
spec wraps long fenced lines on narrow screens only, without changing
desktop rendering, escaping, or content.

## Rules
1. A `<meta name="viewport" content="width=device-width, initial-scale=1">`
   tag in the head, so mobile browsers lay out at device width.
2. The existing `pre` rule is unchanged (desktop keeps `overflow-x:auto`).
3. One media query `@media (max-width:40em)` adds
   `pre{white-space:pre-wrap;overflow-wrap:anywhere}`: below 40 em the
   fenced block wraps long lines instead of scrolling. `anywhere`
   breaks overlong tokens so no line can force horizontal overflow.
4. No JavaScript, no new assets, no change to escaping, structure, or
   the provisional banner. The no-`http`/`https` guarantee still holds
   (the media query is plain CSS).
5. Deterministic: same input, same output.

## Non-goals
Redesigning the report layout, touching report content, responsive
images or fonts.
