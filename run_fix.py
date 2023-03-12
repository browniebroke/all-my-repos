from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from random import randint

import tomli
from all_repos import autofix_lib
from all_repos.grep import repos_matching


UPDATED_RELEASE_PART = """  release:
    runs-on: ubuntu-latest
    environment: release
    needs:
      - test
      - commitlint

    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0

      - name: Release
        uses: relekang/python-semantic-release@v7.33.2
        if: github.ref_name == 'main'
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          pypi_token: ${{ secrets.PYPI_TOKEN }}
      - name: Test release
        uses: relekang/python-semantic-release@v7.33.2
        if: github.ref_name != 'main'
        with:
          additional_options: --noop
"""


def find_repos(config) -> set[str]:
    repos = repos_matching(
        config,
        (
            "relekang/python-semantic-release",
            "--",
            ".github/workflows/ci.yml",
        ),
    )
    print(repos)
    return repos


def apply_fix():
    ci_yml = Path(".github/workflows/ci.yml")
    file_content = ci_yml.read_text()
    if "Test release" in file_content:
        return

    updated_lines = []
    for line in file_content.split("\n"):
        if line == "  release:":
            break
        updated_lines.append(line)

    updated_lines.extend(UPDATED_RELEASE_PART.split("\n"))

    ci_yml.write_text("\n".join(updated_lines))


def main(argv=None):
    parser = argparse.ArgumentParser()
    autofix_lib.add_fixer_args(parser)
    args = parser.parse_args(argv)

    repos, config, commit, autofix_settings = autofix_lib.from_cli(
        args,
        find_repos=find_repos,
        msg=f"ci: run PSR with no-op on feature branch",
        branch_name=f"ci/noop-psr",
    )
    autofix_lib.fix(
        repos,
        apply_fix=apply_fix,
        config=config,
        commit=commit,
        autofix_settings=autofix_settings,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
