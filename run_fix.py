from __future__ import annotations

import argparse
from pathlib import Path

from all_repos import autofix_lib
from all_repos.grep import repos_matching

# Find repos that have this file...
FILE_NAME = ".github/ISSUE_TEMPLATE/2-feature-request.md"
# ... and which content contains this string.
FILE_CONTAINS = "Feature request"
# Git stuff
GIT_COMMIT_MSG = "chore: improve issue templates"
GIT_BRANCH_NAME = "chore/issue-templates"


def apply_fix():
    """Apply fix to a matching repo."""

    templates_path = Path(".github") / "ISSUE_TEMPLATE"
    if not templates_path.exists():
        return

    (templates_path / "1-bug_report.md").unlink(missing_ok=True)
    (templates_path / "2-feature-request.md").unlink(missing_ok=True)

    current_path = Path(__file__).parent

    result = autofix_lib.run("git", "remote", "get-url", "origin", capture_output=True)
    origin_url = result.stdout.decode().strip()
    repo_name = origin_url.split("/")[-1]

    file_names = [
        "1-bug-report.yml",
        "2-feature-request.yml",
        "config.yml",
    ]
    for file_name in file_names:
        content = (current_path / file_name).read_text()
        file_path = templates_path / file_name
        rendered_content = content.replace("{{ repo_name }}", repo_name)
        file_path.write_text(rendered_content)
        autofix_lib.run("git", "add", str(file_path))


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
