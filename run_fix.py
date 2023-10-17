from __future__ import annotations

import argparse
import re
from pathlib import Path

from all_repos import autofix_lib
from all_repos.grep import repos_matching

# Find repos that have this file...
FILE_NAME = "pyproject.toml"
# ... and which content contains this string.
FILE_CONTAINS = "version_variable = \""
# Git stuff
GIT_COMMIT_MSG = "chore: update PSR version_variables config"
GIT_BRANCH_NAME = "chore/psr-version-variables"



def apply_fix():
    """Apply fix to a matching repo."""
    pyproject_toml = Path(FILE_NAME)
    content = pyproject_toml.read_text()
    if "version_variables = [" in content:
        return

    content = re.sub(
        r'version_variable = "([^"]+)"',
        r'version_variables = [\n    "\1",\n]',
        content,
    )

    pyproject_toml.write_text(content)


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
