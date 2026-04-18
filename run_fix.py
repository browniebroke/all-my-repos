from __future__ import annotations

import argparse
from pathlib import Path

from all_repos import autofix_lib
from all_repos.grep import repos_matching

# Find repos that have this file...
FILE_NAMES = [".gitpod.yml"]
# ... and which content contains this string.
FILE_CONTAINS = "tasks"
# Git stuff
GIT_COMMIT_MSG = "chore: remove .gitpot.yml"
GIT_BRANCH_NAME = "chore/remove-gitpod"


def apply_fix():
    """
    Apply fix to a matching repo.

    To run a command in the context of the repo, use autofix_lib.run. For example:

        autofix_lib.run("uv", "sync")
    """
    gitpod_yml = Path(".gitpod.yml")
    gitpod_yml.unlink(missing_ok=True)


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
