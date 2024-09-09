from __future__ import annotations

import argparse
from pathlib import Path

from all_repos import autofix_lib
from all_repos.grep import repos_matching

# Find repos that have this file...
FILE_NAMES = [
    "pyproject.toml",
]
# ... and which content contains this string.
FILE_CONTAINS = "tool.semantic_release.changelog"
# Git stuff
GIT_COMMIT_MSG = "chore: ignore commits with unknown category in PSR "
GIT_BRANCH_NAME = "chore/ignore-unknown-category-commits-psr"

BEFORE_SECTION = """[tool.semantic_release.changelog]
exclude_commit_patterns = [
    "chore*",
    "ci*",
]"""
AFTER_SECTION = """[tool.semantic_release.changelog]
exclude_commit_patterns = [
    "chore.*",
    "ci.*",
    "Merge pull request .*",
]"""

FOR_LOOP_BEFORE = """{%- for category, commits in release["elements"].items() %}"""
FOR_LOOP_AFTER = """{%- for category, commits in release["elements"].items() %}{% if category != "unknown" %}"""

END_FOR_BEFORE = """{%- endfor %}{# for category, commits #}"""
END_FOR_AFTER = """{%- endif %}{% endfor %}{# for category, commits #}"""


def apply_fix():
    """Apply fix to a matching repo."""
    # pyproject.toml
    for file_name in FILE_NAMES:
        file_path = Path(file_name)
        if not file_path.exists():
            continue

        content = file_path.read_text()
        if AFTER_SECTION in content:
            continue

        content = content.replace(BEFORE_SECTION, AFTER_SECTION)
        file_path.write_text(content)

    # changelog template
    file_path = Path("templates/CHANGELOG.md.j2")
    if not file_path.exists():
        return

    content = file_path.read_text()
    if """{% if category != "unknown" %}""" in content:
        return

    content = content.replace(FOR_LOOP_BEFORE, FOR_LOOP_AFTER)
    content = content.replace(END_FOR_BEFORE, END_FOR_AFTER)
    file_path.write_text(content)


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
