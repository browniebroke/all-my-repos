from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from random import randint

import tomli
from all_repos import autofix_lib
from all_repos.grep import repos_matching


REPLACEMENT = """
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.2.0
    hooks:
      - id: debug-statements
      - id: check-builtin-literals
      - id: check-case-conflict
      - id: check-docstring-first
      - id: check-json
      - id: check-toml
      - id: check-xml
      - id: check-yaml
      - id: detect-private-key
      - id: end-of-file-fixer
      - id: trailing-whitespace
"""
replacement_lines = [li for li in REPLACEMENT.split("\n") if li]


def find_repos(config) -> set[str]:
    repos = repos_matching(
        config,
        (
            "https://github.com/pre-commit/pre-commit-hooks",
            "--",
            ".pre-commit-config.yaml",
        ),
    )
    print(repos)
    return repos


def apply_fix():
    config_file = Path(".pre-commit-config.yaml")
    config_text = config_file.read_text()
    if "- id: check-docstring-first" in config_text:
        return
    lines = config_text.split("\n")
    start = lines.index("  - repo: https://github.com/pre-commit/pre-commit-hooks")
    offset = 0
    for line_nb, line in enumerate(lines[start + 1 :]):
        if line.startswith("  - repo:"):
            offset = line_nb
            break
    updated_lines = [*lines[:start], *replacement_lines, *lines[start + offset :]]
    print(updated_lines)
    config_file.write_text("\n".join(updated_lines))


def main(argv=None):
    parser = argparse.ArgumentParser()
    autofix_lib.add_fixer_args(parser)
    args = parser.parse_args(argv)

    repos, config, commit, autofix_settings = autofix_lib.from_cli(
        args,
        find_repos=find_repos,
        msg="chore: add more pre-commit hooks",
        branch_name="chore/pre-commit-hooks-config",
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
