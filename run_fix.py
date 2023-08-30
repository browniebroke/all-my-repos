from __future__ import annotations

import argparse
import re
from pathlib import Path

from all_repos import autofix_lib
from all_repos.grep import repos_matching

# Find repos that have this file...
FILE_NAME = ".pre-commit-config.yaml"
# ... and which content contains this string.
FILE_CONTAINS = "https://github.com/PyCQA/flake8"
# Git stuff
GIT_COMMIT_MSG = "chore: switch linting to Ruff"
GIT_BRANCH_NAME = "chore/lint-ruff"

RUFF_PRECOMMIT_LINES = [
    "  - repo: https://github.com/astral-sh/ruff-pre-commit",
    "    rev: v0.0.286",
    "    hooks:",
    "      - id: ruff",
    "        args: [--fix, --exit-non-zero-on-fix]",
]
RUFF_PYPROJECT_CONTENT = """
[tool.ruff]
target-version = "py38"
line-length = 88
ignore = [
    "D203", # 1 blank line required before class docstring
    "D212", # Multi-line docstring summary should start at the first line
    "D100", # Missing docstring in public module
    "D104", # Missing docstring in public package
    "D107", # Missing docstring in `__init__`
    "D401", # First line of docstring should be in imperative mood
]
select = [
    "B",   # flake8-bugbear
    "D",   # flake8-docstrings
    "C4",  # flake8-comprehensions
    "S",   # flake8-bandit
    "F",   # pyflake
    "E",   # pycodestyle
    "W",   # pycodestyle
    "UP",  # pyupgrade
    "I",   # isort
    "RUF", # ruff specific
]

[tool.ruff.per-file-ignores]
"tests/**/*" = [
    "D100",
    "D101",
    "D102",
    "D103",
    "D104",
    "S101",
]
"""


def apply_fix():
    """Apply fix to a matching repo."""
    _update_pre_commit_config()
    _update_pyproject_toml()
    _remove_flake8_config()
    print("all done")


def _update_pre_commit_config():
    pre_commit_yml = Path(".pre-commit-config.yaml")
    content = pre_commit_yml.read_text()
    if "https://github.com/astral-sh/ruff-pre-commit" in content:
        return

    updated_lines = []
    keep = True
    for line in content.splitlines():
        if line.startswith('exclude: "') and ".all-contributorsrc" not in line:
            line = re.sub(r'"$', '|.all-contributorsrc"', line)

        if "- repo:" in line:
            # Reset to tru for each new repo
            keep = True

        if (
            "https://github.com/asottile/pyupgrade" in line
            or "https://github.com/PyCQA/isort" in line
            or "https://github.com/PyCQA/flake8" in line
            or "https://github.com/PyCQA/bandit" in line
        ):
            # Remove the above linters
            keep = False

        if "https://github.com/psf/black" in line:
            # Insert new config before black
            updated_lines.extend(RUFF_PRECOMMIT_LINES)

        if keep:
            updated_lines.append(line)

    updated_lines.append("")
    pre_commit_yml.write_text("\n".join(updated_lines))


def _update_pyproject_toml():
    pyproject_toml = Path("pyproject.toml")
    content = pyproject_toml.read_text()
    if "[tool.ruff]" in content:
        return

    updated_lines = []
    for line in content.splitlines():
        if line == "[tool.isort]":
            ruff_lines = [ln for ln in RUFF_PYPROJECT_CONTENT.splitlines() if ln]
            updated_lines.extend(ruff_lines)
            if Path("setup.py").exists():
                updated_lines.append('"setup.py" = ["D100"]')
            if Path("conftest.py").exists():
                updated_lines.append('"conftest.py" = ["D100"]')
            if Path("docs/conf.py").exists():
                updated_lines.append('"docs/conf.py" = ["D100"]')
            updated_lines.append("")
            updated_lines.append("[tool.ruff.isort]")
            continue
        if line == 'profile = "black"':
            continue
        if line.startswith("known_first_party ="):
            line = line.replace(
                "known_first_party",
                "known-first-party",
            )
            updated_lines.append(line)
            continue

        updated_lines.append(line)

    updated_lines.append("")
    pyproject_toml.write_text("\n".join(updated_lines))


def _remove_flake8_config():
    flake8_config = Path(".flake8")
    if flake8_config.exists():
        flake8_config.unlink()


# You shouldn't need to change anything below this line


def find_repos(config) -> set[str]:
    """Find matching repos using git grep."""
    repos = repos_matching(
        config,
        (FILE_CONTAINS, "--", FILE_NAME),
    )
    return repos


def main():
    """Entry point."""
    parser = argparse.ArgumentParser()
    autofix_lib.add_fixer_args(parser)
    args = parser.parse_args(None)

    repos, cfg, commit, stg = autofix_lib.from_cli(
        args,
        find_repos=find_repos,
        msg=GIT_COMMIT_MSG,
        branch_name=GIT_BRANCH_NAME,
    )
    autofix_lib.fix(
        repos,
        apply_fix=apply_fix,
        config=cfg,
        commit=commit,
        autofix_settings=stg,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
