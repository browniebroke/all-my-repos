from __future__ import annotations

import argparse
from pathlib import Path

from all_repos import autofix_lib
from all_repos.grep import repos_matching

# Find repos that have this file...
FILE_NAMES = ["pyproject.toml", "project/pyproject.toml.jinja"]
# ... and which content contains this string.
FILE_CONTAINS = "ini_options.pythonpath"
# Git stuff
GIT_COMMIT_MSG = "chore: migrate pytest config to version 9"
GIT_BRANCH_NAME = "chore/pytest-9-config"


def apply_fix():
    """Apply fix to a matching repo."""
    for file_name in FILE_NAMES:
        file_path = Path(file_name)
        if not file_path.exists():
            continue
        file_content = file_path.read_text()

        # Replace old style table
        file_content = file_content.replace("[tool.pytest.ini_options]", "[tool.pytest]")

        # Initialise loop variables
        inside_pytest_section = False
        updated_lines = []

        for line in file_content.splitlines():
            if line == "[tool.pytest]":
                inside_pytest_section = True
            elif line.startswith("[tool.") and not line.startswith("[tool.pytest") and inside_pytest_section:
                inside_pytest_section = False
            elif inside_pytest_section:
                line = line.removeprefix("ini_options.")
            updated_lines.append(line)

        file_path.write_text("\n".join(updated_lines) + "\n")


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
