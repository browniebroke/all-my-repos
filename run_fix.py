from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

from all_repos import autofix_lib
from all_repos.grep import repos_matching

# Find repos that have this file (also matches template's project/ folder)...
FILE_NAMES = ["*.github/workflows/hacktoberfest.yml"]
# ... and which content contains this string.
FILE_CONTAINS = "github_token: ${{ secrets."
# Git stuff
GIT_COMMIT_MSG = "ci: use the built-in token in the Hacktoberfest workflow"
GIT_BRANCH_NAME = "ci/hacktoberfest-token"

OLD_TOKENS = ("secrets.GH_PAT", "secrets.CPR_GITHUB_TOKEN")
NEW_TOKEN = "secrets.GITHUB_TOKEN"
RUNS_ON_RE = re.compile(r"^(?P<indent>[ ]+)runs-on: .*$", re.MULTILINE)
PERMISSIONS = "permissions:\n{indent}  contents: write\n{indent}  issues: write"


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
        if not any(token in content for token in OLD_TOKENS):
            continue
        for token in OLD_TOKENS:
            content = content.replace(token, NEW_TOKEN)
        if "permissions:" not in content:
            content = RUNS_ON_RE.sub(
                lambda m: (
                    f"{m.group(0)}\n{m['indent']}"
                    + PERMISSIONS.format(indent=m["indent"])
                ),
                content,
                count=1,
            )
        path.write_text(content)


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
