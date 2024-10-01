from __future__ import annotations

import argparse
from pathlib import Path

from all_repos import autofix_lib
from all_repos.grep import repos_matching

# Find repos that have this file...
FILE_NAMES = [
    ".pre-commit-config.yaml",
    "project/.pre-commit-config.yaml",
]
# ... and which content contains this string.
FILE_CONTAINS = "https://github.com/python-poetry/poetry"
# Git stuff
GIT_COMMIT_MSG = "chore: add pyproject-fmt to pre-commit config"
GIT_BRANCH_NAME = "chore/add-pyproject-fmt-pre-commit"

BEFORE_SECTION = """  - repo: https://github.com/python-poetry/poetry"""
AFTER_SECTION = """  - repo: https://github.com/tox-dev/pyproject-fmt
    rev: "2.2.3"
    hooks:
      - id: pyproject-fmt
  - repo: https://github.com/python-poetry/poetry"""


def apply_fix():
    """Apply fix to a matching repo."""
    for file_name in FILE_NAMES:
        file_path = Path(file_name)
        if not file_path.exists():
            continue

        content = file_path.read_text()
        if AFTER_SECTION in content:
            continue

        content = content.replace(BEFORE_SECTION, AFTER_SECTION)
        file_path.write_text(content)


# You shouldn't need to change anything below this line


def find_repos(config) -> set[str]:
    """Find matching repos using git grep."""
    repos = repos_matching(
        config,
        (FILE_CONTAINS, "--", *FILE_NAMES),
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
