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
            f"python-version:",
            "--",
            ".github/workflows/ci.yml",
        ),
    )
    print(repos)
    return repos


def apply_fix():
    ci_yml = Path(".github/workflows/ci.yml")
    file_content = ci_yml.read_text()
    if '- "3.11"' in file_content:
        return
    file_content = file_content.replace(
        '          - "3.10"',
        '          - "3.10"\n          - "3.11"',
    )
    ci_yml.write_text(file_content)


def main(argv=None):
    parser = argparse.ArgumentParser()
    autofix_lib.add_fixer_args(parser)
    args = parser.parse_args(argv)

    repos, config, commit, autofix_settings = autofix_lib.from_cli(
        args,
        find_repos=find_repos,
        msg=f"feat: officially support Python 3.11",
        branch_name=f"ci/python3.11",
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
