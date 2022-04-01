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
    repos = repos_matching(config, (":", "--", "package-lock.json"))
    print(repos)
    return repos


CONTENT_TEMPLATE = """name: Upgrader

on:
  workflow_dispatch:
  schedule:
    - cron: '[[MINUTE]] [[HOUR]] [[DAY]] * *'

jobs:
  upgrade:
    uses: browniebroke/github-actions/.github/workflows/npm-upgrade.yml@v1
    secrets:
      gh_pat: ${{ secrets.GH_PERSONAL_ACCESS_TOKEN }}
"""


def apply_fix():
    workflow_file = Path(".github/workflows/npm-upgrade.yml")
    if workflow_file.exists():
        return
    content = CONTENT_TEMPLATE.replace("[[MINUTE]]", str(randint(1, 59)))
    content = content.replace("[[HOUR]]", str(randint(1, 23)))
    content = content.replace("[[DAY]]", str(randint(1, 28)))
    workflow_file.touch()
    workflow_file.write_text(content)
    autofix_lib.run('git', 'add', str(workflow_file))


def main(argv=None):
    parser = argparse.ArgumentParser()
    autofix_lib.add_fixer_args(parser)
    args = parser.parse_args(argv)

    repos, config, commit, autofix_settings = autofix_lib.from_cli(
        args,
        find_repos=find_repos,
        msg="chore: add npm-upgrade workflow",
        branch_name="chore/npm-upgrade",
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
