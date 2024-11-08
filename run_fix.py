from __future__ import annotations

import argparse
from pathlib import Path

from all_repos import autofix_lib
from all_repos.grep import repos_matching

# Find repos that have this file...
FILE_NAMES = [
    ".github/workflows/ci.yml",
    "project/.github/workflows/ci.yml.jinja",
]
# ... and which content contains this string.
FILE_CONTAINS = "python-semantic-release/python-semantic-release"
# Git stuff
GIT_COMMIT_MSG = "ci: ensure release is on the commit as the workflow"
GIT_BRANCH_NAME = "ci/release-git-sha"

PREVIOUS_CHECKOUT = """      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
          ref: ${{ github.head_ref || github.ref_name }}

      # Do a dry run of PSR
      - name: Test release"""
AFTER_CHECKOUT = """      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
          ref: ${{ github.sha }}

      - name: Checkout commit for release
        run: |
          git checkout -B ${{ github.ref_name }} ${{ github.sha }}

      # Do a dry run of PSR
      - name: Test release"""

PREVIOUS_PUBLISH = """      - name: Publish package distributions to GitHub Releases
        uses: python-semantic-release/publish-action@v9.12.2
        if: steps.release.outputs.released == 'true'
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}"""
AFTER_PUBLISH = """      - name: Publish package distributions to GitHub Releases
        uses: python-semantic-release/publish-action@v9.12.2
        if: steps.release.outputs.released == 'true'
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          tag: ${{ steps.release.outputs.tag }}"""


def apply_fix():
    """Apply fix to a matching repo."""
    for file_name in FILE_NAMES:
        file_path = Path(file_name)
        if not file_path.exists():
            continue

        content = file_path.read_text()
        if 'git checkout -B ${{ github.ref_name }} ${{ github.sha }}' in content:
            continue

        content = content.replace(PREVIOUS_CHECKOUT, AFTER_CHECKOUT)
        content = content.replace(PREVIOUS_PUBLISH, AFTER_PUBLISH)

        file_path.write_text(content)

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
