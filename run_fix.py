from __future__ import annotations

import argparse
from pathlib import Path

from all_repos import autofix_lib
from all_repos.grep import repos_matching

# Find repos that have this file...
FILE_NAMES = [".github/workflows/ci.yml"]
# ... and which content contains this string.
FILE_CONTAINS = "j178/prek-action"
# Git stuff
GIT_COMMIT_MSG = "ci: fail lint job if prek fails"
GIT_BRANCH_NAME = "ci/prek-failures"


WITH_PC_LITE = '''        with:
          msg: "chore: auto-fix from pre-commit hooks"'''
WITH_PC_LITE_NEW = '''        if: always()
        with:
          msg: "chore: auto-fix from pre-commit hooks"
      - name: Fail if hooks failed
        if: steps.prek.outcome == 'failure'
        run: exit 1'''

def apply_fix():
    """
    Apply fix to a matching repo.

    To run a command in the context of the repo, use autofix_lib.run. For example:

        autofix_lib.run("uv", "sync")
    """
    file_paths = [
        Path(".github/workflows/ci.yml"),
        Path("project/.github/workflows/ci.yml.jinja"),
    ]
    for ci_yaml in file_paths:
        if not ci_yaml.exists():
            continue
        content = ci_yaml.read_text()
        if "Fail if hooks failed" in content:
            continue

        content = content.replace(
            "        continue-on-error: true",
            "        id: prek\n        continue-on-error: true"
        )
        content = content.replace(WITH_PC_LITE, WITH_PC_LITE_NEW)
        ci_yaml.write_text(content)


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
