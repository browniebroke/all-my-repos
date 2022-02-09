from __future__ import annotations

import argparse
import re
from pathlib import Path

from all_repos import autofix_lib
from all_repos.grep import repos_matching


def find_repos(config) -> set[str]:
    repos = repos_matching(config, ("=", "--", "poetry.lock"))
    print(repos)
    return repos


def apply_fix():
    pre_commit_config = Path(".pre-commit-config.yaml")
    if not pre_commit_config.exists():
        return
    content = pre_commit_config.read_text()
    if "repo: https://github.com/PyCQA/bandit" in content:
        return

    content += "\n".join(
        [
            "  - repo: https://github.com/PyCQA/bandit",
            "    rev: 1.7.2",
            "    hooks:",
            "      - id: bandit",
            "        args: [-x, tests]",
            "",
        ]
    )
    pre_commit_config.write_text(content)


def main(argv=None):
    parser = argparse.ArgumentParser()
    autofix_lib.add_fixer_args(parser)
    args = parser.parse_args(argv)

    repos, config, commit, autofix_settings = autofix_lib.from_cli(
        args,
        find_repos=find_repos,
        msg="chore: add bandit to pre-commit config",
        branch_name="pre-commit-bandit-2",
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
