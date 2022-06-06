from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from random import randint

import tomli
from all_repos import autofix_lib
from all_repos.grep import repos_matching

PACKAGE = "bandit"


def find_repos(config) -> set[str]:
    repos = repos_matching(
        config,
        (
            f"{PACKAGE} = ",
            "--",
            "pyproject.toml",
        ),
    )
    print(repos)
    return repos


def apply_fix():
    autofix_lib.run(
        "poetry",
        "remove",
        "-D",
        PACKAGE,
    )


def main(argv=None):
    parser = argparse.ArgumentParser()
    autofix_lib.add_fixer_args(parser)
    args = parser.parse_args(argv)

    repos, config, commit, autofix_settings = autofix_lib.from_cli(
        args,
        find_repos=find_repos,
        msg=f"chore: remove {PACKAGE} from dev dependencies",
        branch_name=f"remove/{PACKAGE}",
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
