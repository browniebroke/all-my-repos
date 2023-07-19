from __future__ import annotations

import argparse
from pathlib import Path

from all_repos import autofix_lib
from all_repos.grep import repos_matching

# Find repos that have this file...
FILE_NAME = ".github/workflows/ci.yml"
# ... and which content contains this string.
FILE_CONTAINS = 'relekang/python-semantic-release@v8'
# Git stuff
GIT_COMMIT_MSG = "ci: update release phase to accommodate changes in PSR v8"
GIT_BRANCH_NAME = "ci/psr-v8-release"

UPDATED_CONTENT = """  release:
    runs-on: ubuntu-latest
    environment: release
    needs:
      - test
      - commitlint

    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0
          ref: ${{ github.head_ref || github.ref_name }}

      # Do a dry run of PSR
      - name: Test release
        uses: relekang/python-semantic-release@v8.0.2
        if: github.ref_name != 'main'
        with:
          root_options: --noop

      # On main branch: actual PSR + upload to PyPI & GitHub
      - name: Release
        uses: relekang/python-semantic-release@v8.0.2
        id: release
        if: github.ref_name == 'main'
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}

      - name: Publish package distributions to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        if: steps.release.outputs.released == 'true'
        with:
          password: ${{ secrets.PYPI_TOKEN }}

      - name: Publish package distributions to GitHub Releases
        uses: python-semantic-release/upload-to-gh-release@main
        if: steps.release.outputs.released == 'true'
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
"""


def apply_fix():
    """Apply fix to a matching repo."""
    ci_yml = Path(".github/workflows/ci.yml")
    content = ci_yml.read_text()
    if "pypa/gh-action-pypi-publish" in content:
        return

    # read until release phase
    updated_lines = []
    for line in content.splitlines():
        if line == "  release:":
            break
        updated_lines.append(line)

    # add new release phase
    updated_lines.extend(UPDATED_CONTENT.splitlines())

    # write back content
    new_content = "\n".join(updated_lines)
    ci_yml.write_text(new_content)
    breakpoint()


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
