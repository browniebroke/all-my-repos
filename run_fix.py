from __future__ import annotations

import argparse
from pathlib import Path

from all_repos import autofix_lib
from all_repos.grep import repos_matching

# Find repos that have this file...
FILE_NAMES = [".pre-commit-config.yaml", "project/.pre-commit-config.yaml.jinja"]
# ... and which content contains this string.
FILE_CONTAINS = "https://github.com/pre-commit/mirrors-mypy"
# Git stuff
GIT_COMMIT_MSG = "chore: move mypy to local hook with django stubs"
GIT_BRANCH_NAME = "chore/mypy-local-hook"

PRE_COMMIT_BEFORE = """  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v2.3.0
    hooks:
      - id: mypy
        additional_dependencies: []"""
PRE_COMMIT_AFTER = """  - repo: local
    hooks:
      - id: local-mypy
        name: mypy check
        entry: uv run mypy src
        require_serial: true
        language: system
        pass_filenames: false"""


def apply_fix():
    """
    Apply fix to a matching repo.

    To run a command in the context of the repo, use autofix_lib.run. For example:

        autofix_lib.run("uv", "sync")
    """
    # pre-commit config
    for pre_commit_cfg in FILE_NAMES:
        pre_commit_cfg = Path(pre_commit_cfg)
        if not pre_commit_cfg.exists():
            continue
        content = pre_commit_cfg.read_text()
        if "https://github.com/pre-commit/mirrors-mypy" not in content:
            continue

        content = content.replace(PRE_COMMIT_BEFORE, PRE_COMMIT_AFTER)
        pre_commit_cfg.write_text(content)

    # pyproject.toml
    file_paths = [
        Path("pyproject.toml"),
        Path("project/pyproject.toml.jinja"),
    ]
    for idx, pyproject_toml in enumerate(file_paths):
        if not pyproject_toml.exists():
            continue

        content = pyproject_toml.read_text()
        if 'mypy_django_plugin.main' in content:
            continue

        content = content.replace("[tool.mypy]", '[tool.mypy]\nplugins = [ "mypy_django_plugin.main" ]')
        content = content.replace('[dependency-groups]\ndev = [', '[dependency-groups]\ndev = [\n  "django-stubs>=6.0.9",\n  "mypy>=2.3",')
        content = content.replace('[tool.pytest]', '[tool.django-stubs]\ndjango_settings_module = "tests.settings"\n\n[tool.pytest]')
        pyproject_toml.write_text(content)

        if idx == 0:
            autofix_lib.run("uv", "lock")


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
