from __future__ import annotations

import argparse
from pathlib import Path

from all_repos import autofix_lib
from all_repos.grep import repos_matching

# Find repos that have this file...
FILE_NAME = ".github/labels.toml"
# ... and which content contains this string.
FILE_CONTAINS = 'breaking'
# Git stuff
GIT_COMMIT_MSG = "chore: add fund to list of labels"
GIT_BRANCH_NAME = "chore/add-fund-label"


def apply_fix():
    """Apply fix to a matching repo."""
    new_content = (Path(__file__).parent / "labels.toml").read_text()

    labels_toml = Path(FILE_NAME)
    if labels_toml.exists():
        labels_toml.write_text(new_content)

    # Update pyproject template
    labels_toml = Path(f"project/{FILE_NAME}")
    if labels_toml.exists():
        labels_toml.write_text(new_content)


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
