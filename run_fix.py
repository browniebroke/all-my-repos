from __future__ import annotations

import argparse
from pathlib import Path

from all_repos import autofix_lib
from all_repos.grep import repos_matching

# Find repos that have this file...
FILE_NAMES = [".github/workflows/labels.yml"]
# ... and which content contains this string.
FILE_CONTAINS = "secrets.GH_PAT"
# Git stuff
GIT_COMMIT_MSG = "chore: remove long-lived GitHub PAT in labels workflow"
GIT_BRANCH_NAME = "chore/remove-gh-pat"

RUN_STEP_OLD = """
    runs-on: ubuntu-latest
    steps:"""
RUN_STEPS_UPDATED  = """
    runs-on: ubuntu-latest
    permissions:
      contents: read
      issues: write
    steps:"""


def apply_fix():
    """
    Apply fix to a matching repo.

    To run a command in the context of the repo, use autofix_lib.run. For example:

        autofix_lib.run("uv", "sync")
    """
    # pre-commit config
    file_paths = [
        Path(".github/workflows/labels.yml")
    ]
    for labels_yml in file_paths:
        if not labels_yml.exists():
            continue
        content = labels_yml.read_text()
        if "secrets.GH_PAT" not in content:
            continue

        content = content.replace(RUN_STEP_OLD, RUN_STEPS_UPDATED)
        content = content.replace("secrets.GH_PAT", "secrets.GITHUB_TOKEN")
        labels_yml.write_text(content)


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
