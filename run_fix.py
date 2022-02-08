from __future__ import annotations

import argparse
import re
from pathlib import Path

from all_repos import autofix_lib
from all_repos.grep import repos_matching


def find_repos(config) -> set[str]:
    repos = repos_matching(config, ("pyupgrade =", "--", "pyproject.toml"))
    print(repos)
    return repos


def apply_fix():
    pyproject_toml = Path("pyproject.toml")
    content = pyproject_toml.read_text()
    if 'pyupgrade = "^2.31"' in content:
        return
    content = re.sub(r'pyupgrade = ".+"', 'pyupgrade = "^2.31"', content)
    pyproject_toml.write_text(content)
    autofix_lib.run("poetry", "lock")


def main(argv=None):
    parser = argparse.ArgumentParser()
    autofix_lib.add_fixer_args(parser)
    args = parser.parse_args(argv)

    repos, config, commit, autofix_settings = autofix_lib.from_cli(
        args,
        find_repos=find_repos,
        msg="chore: upgrade to latest pyupgrade",
        branch_name="upgrade-pyupgrade",
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
