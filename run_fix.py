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
            "poetry.core.masonry.api",
            "--",
            "pyproject.toml",
        ),
    )
    print(repos)
    return repos


TO_ADD = "\n".join(
    [
        "  - repo: https://github.com/python-poetry/poetry",
        "    rev: 1.2.2",
        "    hooks:",
        "      - id: poetry-check",
    ]
)


def apply_fix():
    pre_commit_config_yml = Path(".pre-commit-config.yaml")
    if not pre_commit_config_yml.exists():
        return

    pre_commit_config = pre_commit_config_yml.read_text()
    pre_commit_config = pre_commit_config.replace(
        "  - repo: https://github.com/pre-commit/mirrors-prettier",
        f"{TO_ADD}\n  - repo: https://github.com/pre-commit/mirrors-prettier",
    )

    pre_commit_config_yml.write_text(pre_commit_config)


def main(argv=None):
    parser = argparse.ArgumentParser()
    autofix_lib.add_fixer_args(parser)
    args = parser.parse_args(argv)

    repos, config, commit, autofix_settings = autofix_lib.from_cli(
        args,
        find_repos=find_repos,
        msg="chore: add poetry check pre-commit hook",
        branch_name=f"chore/poetry-check-pre-commit",
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
