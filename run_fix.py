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
            "tool.poetry.urls",
            "--",
            "pyproject.toml",
        ),
    )
    print(repos)
    return repos


def apply_fix():
    pyproject_toml = Path("pyproject.toml")
    if "Twitter" in (content := pyproject_toml.read_text()):
        return

    lines = content.splitlines()
    in_section = False
    out_lines = []
    for line in lines:
        if in_section and line == "":
            out_lines.extend(
                [
                    '"Twitter" = "https://twitter.com/_BrunoAlla"',
                    '"Mastodon" = "https://fosstodon.org/@browniebroke"',
                ]
            )
            in_section = False
        if line == "[tool.poetry.urls]":
            in_section = True
        out_lines.append(line)

    out_lines.append("")
    pyproject_toml.write_text("\n".join(out_lines))


def main(argv=None):
    parser = argparse.ArgumentParser()
    autofix_lib.add_fixer_args(parser)
    args = parser.parse_args(argv)

    repos, config, commit, autofix_settings = autofix_lib.from_cli(
        args,
        find_repos=find_repos,
        msg="chore: add links to social media on PyPI",
        branch_name=f"chore/links-social-media-pypi",
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
