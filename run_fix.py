from __future__ import annotations

import argparse
from pathlib import Path

from all_repos import autofix_lib
from all_repos.grep import repos_matching

# Find repos that have this file...
FILE_NAME = "pyproject.toml"
# ... and which content contains this string.
FILE_CONTAINS = "tool.ruff"
# Git stuff
GIT_COMMIT_MSG = "chore: upgrade ruff settings"
GIT_BRANCH_NAME = "chore/upgrade-ruff-settings"


def apply_fix():
    """Apply fix to a matching repo."""
    pyproject_toml = Path("pyproject.toml")
    file_content = pyproject_toml.read_text()
    if "[tool.ruff.lint]" in file_content:
        return

    updated_lines = []
    inside_ruff = False
    inside_lint_section = False
    for line in file_content.splitlines():
        if line == "[tool.ruff]":
            inside_ruff = True

        if inside_ruff and not inside_lint_section and line.startswith("ignore = ["):
            inside_lint_section = True
            updated_lines.append("")
            updated_lines.append("[tool.ruff.lint]")
            updated_lines.append(line)
            continue

        if inside_lint_section and line == "[tool.ruff.per-file-ignores]":
            if updated_lines[-1] != "":
                updated_lines.append("")
            updated_lines.append("[tool.ruff.lint.per-file-ignores]")
            continue

        if inside_lint_section and line == "[tool.ruff.isort]":
            if updated_lines[-1] != "":
                updated_lines.append("")
            updated_lines.append("[tool.ruff.lint.isort]")
            continue

        updated_lines.append(line)

    # Add newline at end of file
    updated_lines.append("")
    pyproject_toml.write_text("\n".join(updated_lines))


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
