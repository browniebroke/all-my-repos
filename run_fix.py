from __future__ import annotations

import argparse
from pathlib import Path

from all_repos import autofix_lib
from all_repos.grep import repos_matching

CONTENT = """module.exports = {
  extends: ["@commitlint/config-conventional"],
  rules: {
    "header-max-length": [0, "always", Infinity],
    "body-max-line-length": [0, "always", Infinity],
    "footer-max-line-length": [0, "always", Infinity],
  },
};
"""


def find_repos(config) -> set[str]:
    repos = repos_matching(
        config,
        (
            "config-conventional",
            "--",
            "commitlint.config.js",
        ),
    )
    print(repos)
    return repos


def apply_fix():
    file_path = Path("commitlint.config.js")
    file_path.write_text(CONTENT)


def main(argv=None):
    parser = argparse.ArgumentParser()
    autofix_lib.add_fixer_args(parser)
    args = parser.parse_args(argv)

    repos, config, commit, autofix_settings = autofix_lib.from_cli(
        args,
        find_repos=find_repos,
        msg=(
            "chore: update commitlint config to be more permissive"
        ),
        branch_name=f"chore/commitlint-cfg",
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
