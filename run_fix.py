from __future__ import annotations
import argparse
import re
from pathlib import Path

from all_repos import autofix_lib
from all_repos.grep import repos_matching


def find_repos(config) -> set[str]:
    repos = repos_matching(config, ("black =", "--", "pyproject.toml"))
    return repos


def apply_fix():
    pyproject_toml = Path("pyproject.toml")
    content = pyproject_toml.read_text()
    if 'black = {version = "^22.1"' in content or 'black = "^22.1"' in content:
        return
    content = content.replace(
        'black = {version = "^21.9b0"',
        'black = {version = "^22.1"'
    )
    content = re.sub(r'black = ".+"', 'black = "^22.1"', content)
    pyproject_toml.write_text(content)
    autofix_lib.run("poetry", "lock")


def main(argv=None):
    parser = argparse.ArgumentParser()
    autofix_lib.add_fixer_args(parser)
    args = parser.parse_args(argv)

    repos, config, commit, autofix_settings = autofix_lib.from_cli(
        args,
        find_repos=find_repos,
        msg="chore: upgrade to black stable",
        branch_name="upgrade-black-stable",
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
