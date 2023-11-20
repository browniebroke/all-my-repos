from __future__ import annotations

import argparse
from pathlib import Path

from all_repos import autofix_lib
from all_repos.grep import repos_matching

# Find repos that have this file...
FILE_NAME = "pyproject.toml"
# ... and which content contains this string.
FILE_CONTAINS = "tool.semantic_release"
# Git stuff
GIT_COMMIT_MSG = "chore: add PSR branch groups to test releases on feature branches"
GIT_BRANCH_NAME = "chore/psr-branch-groups"

LINES_TO_INSERT = """[tool.semantic_release.branches.main]
match = "main"

[tool.semantic_release.branches.noop]
match = "(?!main$)"
prerelease = true

"""


def apply_fix():
    """Apply fix to a matching repo."""
    pyproject_toml = Path("pyproject.toml")
    file_content = pyproject_toml.read_text()
    if "tool.semantic_release.branches.main" in file_content:
        return

    breakpoint()
    updated_lines = []
    inside_psr = False
    branch_line_removed = False
    for line in file_content.splitlines():
        if line == "[tool.semantic_release]":
            inside_psr = True

        if inside_psr and not branch_line_removed and line == 'branch = "main"':
            branch_line_removed = True
            continue

        if line == "[tool.pytest.ini_options]":
            updated_lines.extend(LINES_TO_INSERT.splitlines())
            inside_psr = False

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
