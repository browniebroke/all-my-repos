from __future__ import annotations

import argparse
import re
from pathlib import Path

from all_repos import autofix_lib
from all_repos.grep import repos_matching


def find_repos(config) -> set[str]:
    repos = repos_matching(config, ('python = "^3.6"', "--", "pyproject.toml"))
    print(repos)
    return repos


def apply_fix():
    pyproject_toml = Path("pyproject.toml")
    content = pyproject_toml.read_text()
    if 'python = "^3.7"' in content:
        return
    content = content.replace('python = "^3.6"', 'python = "^3.7"')
    pyproject_toml.write_text(content)
    autofix_lib.run("poetry", "lock")


def main(argv=None):
    parser = argparse.ArgumentParser()
    autofix_lib.add_fixer_args(parser)
    args = parser.parse_args(argv)

    repos, config, commit, autofix_settings = autofix_lib.from_cli(
        args,
        find_repos=find_repos,
        msg="feat: drop Python 3.6",
        branch_name="drop-python3.6",
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
