from __future__ import annotations

import argparse

from all_repos import autofix_lib
from all_repos.grep import repos_matching


def find_repos(config) -> set[str]:
    return repos_matching(
        config, ('build-backend = "poetry.core.masonry.api"', "--", "pyproject.toml")
    )


def apply_fix():
    autofix_lib.run("poetry", "update", "-n")


def main(argv=None):
    parser = argparse.ArgumentParser()
    autofix_lib.add_fixer_args(parser)
    args = parser.parse_args(argv)

    repos, config, commit, autofix_settings = autofix_lib.from_cli(
        args,
        find_repos=find_repos,
        msg="chore: update dependencies",
        branch_name="poetry-date",
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
