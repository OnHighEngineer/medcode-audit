"""Pin repo metadata and the README's front-door API names.

Two drift classes the decision log records catching by hand:
requires-python contradicting the CI matrix (fixed 2026-11-14) and
README claims about how the suite runs. A third needs no history:
every `from medcode_audit...` name the README tells a reviewer to
import must still exist, or the front door breaks silently.
"""
import re
from importlib import import_module
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = (ROOT / 'pyproject.toml').read_text()
CI = (ROOT / '.github' / 'workflows' / 'ci.yml').read_text()
README = (ROOT / 'README.md').read_text()


def test_requires_python_floor_matches_the_ci_matrix():
    assert 'requires-python = ">=3.10' in PYPROJECT
    assert "'3.10'" in CI and "'3.11'" in CI


def test_ci_runs_pytest_on_push_and_pull_request_to_main():
    assert 'push:' in CI and 'pull_request:' in CI
    assert 'branches: [main]' in CI
    assert 'python -m pytest -q' in CI


def test_pyproject_points_pytest_at_src_and_tests():
    # README tells reviewers to run `python -m pytest -q` from the root.
    assert 'testpaths = ["tests"]' in PYPROJECT
    assert 'pythonpath = ["src"]' in PYPROJECT


def test_readme_snippet_api_names_still_import():
    imports = re.findall(r'from medcode_audit\.(\w+) import ([\w, ]+)',
                         README)
    assert imports, 'README must show reviewer-facing imports'
    for module_name, names in imports:
        module = import_module(f'medcode_audit.{module_name}')
        for name in (n.strip() for n in names.split(',')):
            assert hasattr(module, name), (
                f'README imports medcode_audit.{module_name}.{name}, '
                'which no longer exists')
