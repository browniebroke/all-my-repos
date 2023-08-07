from __future__ import annotations

import argparse
import re
from pathlib import Path

from all_repos import autofix_lib
from all_repos.grep import repos_matching

# Find repos that have this file...
FILE_NAME = ".github/workflows/labels.yml"
# ... and which content contains this string.
FILE_CONTAINS = 'python-version: 3'
# Git stuff
GIT_COMMIT_MSG = "ci: use latest Python 3 for labels workflow"
GIT_BRANCH_NAME = "ci/labels-latest-python"


def apply_fix():
    """Apply fix to a matching repo."""
    ci_yml = Path(".github/workflows/labels.yml")
    content = ci_yml.read_text()
    content = re.sub(
        r'python-version: 3.\d+',
        'python-version: 3.x',
        content,
    )
    ci_yml.write_text(content)


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
