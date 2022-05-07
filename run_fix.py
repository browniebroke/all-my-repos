from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from random import randint

import tomli
from all_repos import autofix_lib
from all_repos.grep import repos_matching


TO_INSERT = """
  - repo: https://github.com/codespell-project/codespell
    rev: v2.1.0
    hooks:
      - id: codespell
"""
lines_to_insert = [li for li in TO_INSERT.split("\n") if li]


def find_repos(config) -> set[str]:
    repos = repos_matching(
        config,
        (
            "PyCQA/flake8",
            "--",
            ".pre-commit-config.yaml",
        ),
    )
    print(repos)
    return repos


def apply_fix():
    config_file = Path(".pre-commit-config.yaml")
    config_text = config_file.read_text()
    if "- id: codespell" in config_text:
        return
    lines = config_text.split("\n")
    insert_at = lines.index("  - repo: https://github.com/PyCQA/flake8")
    updated_lines = [
        *lines[:insert_at],
        *lines_to_insert,
        *lines[insert_at:],
    ]
    print(updated_lines)
    config_file.write_text("\n".join(updated_lines))


def main(argv=None):
    parser = argparse.ArgumentParser()
    autofix_lib.add_fixer_args(parser)
    args = parser.parse_args(argv)

    repos, config, commit, autofix_settings = autofix_lib.from_cli(
        args,
        find_repos=find_repos,
        msg="chore: add codespell to pre-commit hooks",
        branch_name="chore/codespell",
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
