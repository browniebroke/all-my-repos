from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from all_repos import autofix_lib
from all_repos.grep import repos_matching

# Find repos that have this file (also matches template's project/ folder)...
FILE_NAMES = ["*.github/workflows/labels.yml"]
# ... and which content contains this string.
FILE_CONTAINS = "uvx labels "
# Git stuff
GIT_COMMIT_MSG = "chore: use labels fork ignoring archived labels"
GIT_BRANCH_NAME = "chore/labels-fork"

OLD_COMMAND = "uvx labels "
NEW_COMMAND = (
    "uvx --with https://github.com/browniebroke/labels/archive/fix/ignore-archived-at.zip"
    " labels "
)


def _should_fix_repo(repo: Path) -> bool:
    """
    Do further filtering on each repo.

    Return:
    - True for repos where the fix should run
    - False for repos where the fix should be skipped
    """
    return True


def apply_fix():
    """
    Apply fix to a matching repo.

    To run a command in the context of the repo, use autofix_lib.run. For example:

        autofix_lib.run("uv", "sync")
    """
    files = subprocess.check_output(
        ["git", "ls-files", "--", *FILE_NAMES], text=True
    ).splitlines()
    for file_name in files:
        path = Path(file_name)
        content = path.read_text()
        path.write_text(content.replace(OLD_COMMAND, NEW_COMMAND))


# You shouldn't need to change anything below this line


def find_repos(config) -> set[str]:
    """Find matching repos using git grep."""
    repos = repos_matching(
        config,
        (FILE_CONTAINS, "--", *FILE_NAMES),
    )
    return {repo for repo in repos if _should_fix_repo(Path(repo))}


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
