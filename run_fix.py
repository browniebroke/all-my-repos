from __future__ import annotations

import argparse
import os
import re
from pathlib import Path

from all_repos import autofix_lib
from all_repos.grep import repos_matching

# Find repos that have this file...
FILE_NAME = ".github/workflows/ci.yml"
# ... and which content contains this string.
FILE_CONTAINS = "actions/checkout@8ad"
# Git stuff
GIT_COMMIT_MSG = "chore: change checkout action to v4 tag"
GIT_BRANCH_NAME = "chore/checkout-action-v4"


def apply_fix():
    """Apply fix to a matching repo."""
    workflows_dir = Path(".github/workflows")
    list_dir = os.listdir(workflows_dir)
    for file_name in list_dir:
        workflow_file_path = workflows_dir / file_name
        if workflow_file_path.suffix == ".yml":
            file_content = workflow_file_path.read_text()
            if "actions/checkout@8ad" not in file_content:
                continue

            file_content = re.sub(
                r'actions/checkout@.*',
                r'actions/checkout@v4',
                file_content,
            )

            workflow_file_path.write_text(file_content)


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
