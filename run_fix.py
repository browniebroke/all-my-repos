from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from random import randint

import tomli
from all_repos import autofix_lib
from all_repos.grep import repos_matching


def find_repos(config) -> set[str]:
    repos = repos_matching(
        config,
        (
            "snok/install-poetry@v1.3.3",
            "--",
            ".github/workflows/ci.yml",
        ),
    )
    print(repos)
    return repos


def apply_fix():
    ci_yml = Path(".github/workflows/ci.yml")
    ci_yml_contents = ci_yml.read_text()
    if (
        "          - ubuntu-latest\n"
        "          - windows-latest\n"
        "          - macOS-latest" in ci_yml_contents
    ):
        return
    ci_yml_contents = ci_yml_contents.replace(
        # Source
        "          - ubuntu-latest\n          - macOS-latest",
        # Replacement
        "          - ubuntu-latest\n"
        "          - windows-latest\n"
        "          - macOS-latest",
    )
    ci_yml.write_text(ci_yml_contents)


def main(argv=None):
    parser = argparse.ArgumentParser()
    autofix_lib.add_fixer_args(parser)
    args = parser.parse_args(argv)

    repos, config, commit, autofix_settings = autofix_lib.from_cli(
        args,
        find_repos=find_repos,
        msg="ci: add windows back to the build matrix",
        branch_name=f"ci/add-windows",
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
