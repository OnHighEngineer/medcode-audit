"""Pin the README's verbatim claims against the committed artifacts.

flow.md (day 27) states the README quotes the demo's tally lines
verbatim, and the week-5 consistency read (decision-log 2026-11-16)
found a README lane bullet naming a snapshot file that did not exist -
drift caught by hand. These tests pin both invariants so doc drift
fails loudly instead of waiting for the weekly read.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / 'README.md'
ARTIFACT = ROOT / 'docs' / 'reviews' / 'day-27-demo-output.md'
SNAPSHOT_DIR = ROOT / 'data' / 'regression'


def _headline_block(readme_text):
    """Return the non-empty lines of the fenced block after 'Headline'."""
    marker = readme_text.find('Headline')
    assert marker != -1, 'README must carry the day-27 headline block'
    rest = readme_text[marker:]
    block = rest.split('```', 2)[1]
    return [line for line in block.splitlines() if line.strip()]


def test_readme_headline_tally_lines_appear_verbatim_in_committed_artifact():
    artifact = ARTIFACT.read_text()
    lines = _headline_block(README.read_text())
    assert lines, 'README headline block must not be empty'
    for line in lines:
        assert line in artifact, (
            f'README headline line missing from {ARTIFACT.name}: {line}')


def test_readme_names_every_committed_snapshot_file():
    readme = README.read_text()
    snapshots = sorted(p.name for p in SNAPSHOT_DIR.glob('*.json'))
    assert snapshots, 'expected committed snapshot files'
    for name in snapshots:
        assert name in readme, f'committed snapshot not named in README: {name}'
