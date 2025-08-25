from __future__ import annotations

import argparse
from pathlib import Path

from all_repos import autofix_lib
from all_repos.grep import repos_matching

# Find repos that have this file...
FILE_NAMES = ["pyproject.toml"]
# ... and which content contains this string.
FILE_CONTAINS = "setuptools.build_meta"
# Git stuff
GIT_COMMIT_MSG = "fix: use SPDX expression for license"
GIT_BRANCH_NAME = "fix/spdx-license"


def apply_fix():
    """Apply fix to a matching repo."""
    pyproject_toml = Path("pyproject.toml")
    content = pyproject_toml.read_text()
    if (
        'requires = [ "setuptools>=77.0.3" ]' in content
        and 'license = "MIT"' in content
    ):
        return

    content = content.replace(
        # From
        'requires = [ "setuptools" ]',
        # To
        'requires = [ "setuptools>=77.0.3" ]',
    )
    content = content.replace(
        'license = { text = "MIT" }',
        'license = "MIT"',
    )
    pyproject_toml.write_text(content)
    print("Done with repo")


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
