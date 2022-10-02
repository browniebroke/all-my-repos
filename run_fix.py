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
            f"example:",
            "--",
            ".github/workflows/hacktoberfest.yml",
        ),
    )
    print(repos)
    return repos


def apply_fix():
    file_path = Path(".github/workflows/hacktoberfest.yml")
    file_content = file_path.read_text()
    file_content = file_content.replace("  example:", "  hacktoberfest:")
    file_path.write_text(file_content)



def main(argv=None):
    parser = argparse.ArgumentParser()
    autofix_lib.add_fixer_args(parser)
    args = parser.parse_args(argv)

    repos, config, commit, autofix_settings = autofix_lib.from_cli(
        args,
        find_repos=find_repos,
        msg=f"chore: update hacktoberfest workflow",
        branch_name=f"update-hacktoberfest-workflow",
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
