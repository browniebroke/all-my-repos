from __future__ import annotations

import argparse
from pathlib import Path

from all_repos import autofix_lib
from all_repos.grep import repos_matching

# Find repos that have this file...
FILE_NAME = ".github/workflows/ci.yml"
# ... and which content contains this string.
FILE_CONTAINS = "snok/install-poetry"
# Git stuff
GIT_COMMIT_MSG = "ci: enable Poetry cache"
GIT_BRANCH_NAME = "ci/poetry-cache"


def apply_fix():
    """Apply fix to a matching repo."""
    file_path = Path(FILE_NAME)
    file_content = file_path.read_text()
    if "snok/install-poetry" not in file_content:
        return

    updated_lines = []
    inside_test = False
    for line in file_content.splitlines():
        if line == "  test:":
            inside_test = True

        if inside_test and "- name: Set up Python" in line:
            updated_lines.append("      - name: Install poetry")
            updated_lines.append("        run: pipx install poetry")

        if inside_test and "- uses: snok/install-poetry" in line:
            continue

        if (
            inside_test
            and "python-version:" in line
            and "with:" in updated_lines[-1]
            and "uses: actions/setup-python" in updated_lines[-2]
        ):
            updated_lines.append("          cache: poetry")

        updated_lines.append(line)

    updated_lines.append("")
    file_path.write_text("\n".join(updated_lines))


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
