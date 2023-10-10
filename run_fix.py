from __future__ import annotations

import argparse
from pathlib import Path

from all_repos import autofix_lib
from all_repos.grep import repos_matching

# Find repos that have this file...
FILE_NAME = ".github/workflows/ci.yml"
# ... and which content contains this string.
FILE_CONTAINS = "PYPI_TOKEN"
# Git stuff
GIT_COMMIT_MSG = "ci: release to PyPI using Trusted Publisher"
GIT_BRANCH_NAME = "ci/trusted-publisher"

CONTENT = """\
  release:
    needs:
      - test
      - commitlint

    runs-on: ubuntu-latest
    environment: release
    concurrency: release
    permissions:
      id-token: write
      contents: write

    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
          ref: ${{ github.head_ref || github.ref_name }}

      # Do a dry run of PSR
      - name: Test release
        uses: python-semantic-release/python-semantic-release@v8.1.1
        if: github.ref_name != 'main'
        with:
          root_options: --noop

      # On main branch: actual PSR + upload to PyPI & GitHub
      - name: Release
        uses: python-semantic-release/python-semantic-release@v8.1.1
        id: release
        if: github.ref_name == 'main'
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}

      - name: Publish package distributions to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        if: steps.release.outputs.released == 'true'

      - name: Publish package distributions to GitHub Releases
        uses: python-semantic-release/upload-to-gh-release@main
        if: steps.release.outputs.released == 'true'
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
"""


def apply_fix():
    """Apply fix to a matching repo."""
    ci_yml = Path(FILE_NAME)
    content = ci_yml.read_text()
    if "secrets.PYPI_TOKEN" not in content:
        return

    new_lines = []
    for line in content.splitlines():
        if "  release:" in line:
            break
        new_lines.append(line)

    new_lines.extend(CONTENT.splitlines())

    ci_yml.write_text("\n".join(new_lines))


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
