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
            f"snok/install-poetry",
            "--",
            ".github/workflows/ci.yml",
        ),
    )
    print(repos)
    return repos


def apply_fix():
    file_path = Path(".github/workflows/ci.yml")
    file_content = file_path.read_text()
    if "snok/install-poetry@v1.3.1" in file_content:
        return
    file_content = file_content.replace(
        "snok/install-poetry@v1",
        "snok/install-poetry@v1.3.1",
    )
    file_path.write_text(file_content)



def main(argv=None):
    parser = argparse.ArgumentParser()
    autofix_lib.add_fixer_args(parser)
    args = parser.parse_args(argv)

    repos, config, commit, autofix_settings = autofix_lib.from_cli(
        args,
        find_repos=find_repos,
        msg=f"chore: reference snok/install-poetry action by full version",
        branch_name=f"fix/install-poetry-version",
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
