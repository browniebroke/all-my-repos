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
            f"https://img.shields.io/github/workflow/status/",
            "--",
            "README.md",
        ),
    )
    print(repos)
    return repos


def apply_fix():
    readme = Path("README.md")
    file_content = readme.read_text()
    if "https://img.shields.io/github/workflow/status/" not in file_content:
        return

    file_content = file_content.replace(
        "https://img.shields.io/github/workflow/status/",
        "https://img.shields.io/github/actions/workflow/status/",
    )
    file_content = file_content.replace("/CI/main?label=", "/ci.yml?branch=main&label=")
    readme.write_text(file_content)


def main(argv=None):
    parser = argparse.ArgumentParser()
    autofix_lib.add_fixer_args(parser)
    args = parser.parse_args(argv)

    repos, config, commit, autofix_settings = autofix_lib.from_cli(
        args,
        find_repos=find_repos,
        msg=f"docs: update badge for CI workflow",
        branch_name=f"docs/fix-ci-badge",
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
