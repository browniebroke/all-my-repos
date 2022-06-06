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
            "relekang/python-semantic-release@v7.29",
            "--",
            ".github/workflows/ci.yml",
        ),
    )
    print(repos)
    return repos


def apply_fix():
    ci_workflow = Path(".github/workflows/ci.yml")
    content = ci_workflow.read_text()
    content = content.replace(
        "relekang/python-semantic-release@v7.29.1",
        "relekang/python-semantic-release@v7.28.1",
    )
    ci_workflow.write_text(content)

    sr_workflow = Path(".github/workflows/semantic-release.yml")
    if sr_workflow.exists():
        content = sr_workflow.read_text()
        content = content.replace(
            "relekang/python-semantic-release@v7.29.1",
            "relekang/python-semantic-release@v7.28.1",
        )
        sr_workflow.write_text(content)


def main(argv=None):
    parser = argparse.ArgumentParser()
    autofix_lib.add_fixer_args(parser)
    args = parser.parse_args(argv)

    repos, config, commit, autofix_settings = autofix_lib.from_cli(
        args,
        find_repos=find_repos,
        msg="fix(deps): revert PSR upgrade",
        branch_name="fix/revert-psr-upgrade",
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
