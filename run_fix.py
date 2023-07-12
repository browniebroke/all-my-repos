from __future__ import annotations

import argparse
from pathlib import Path

from all_repos import autofix_lib
from all_repos.grep import repos_matching

# Find repos that have this file...
FILE_NAME = "pyproject.toml"
# ... and which content contains this string.
FILE_CONTAINS = "sphinx-rtd-theme"
# Git stuff
GIT_COMMIT_MSG = "docs: switch to furo theme"
GIT_BRANCH_NAME = "docs/furo-theme"


def apply_fix():
    """Apply fix to a matching repo."""
    breakpoint()
    pyproject_toml = Path("pyproject.toml")
    content = pyproject_toml.read_text()
    content = content.replace(
        'sphinx-rtd-theme = ">=1.0"',
        'furo = ">=2023.5.20"',
    )
    pyproject_toml.write_text(content)

    docs_conf_py = Path("docs/conf.py")
    content = docs_conf_py.read_text()
    content = content.replace(
        'html_theme = "sphinx_rtd_theme"',
        'html_theme = "furo"',
    )
    docs_conf_py.write_text(content)

    autofix_lib.run(
        "poetry",
        "lock",
        "--no-update",
    )


# You shouldn't need to change anything below this line


def find_repos(config) -> set[str]:
    """Find matching repos using git grep."""
    repos = repos_matching(
        config,
        (FILE_CONTAINS, "--", FILE_NAME),
    )
    return repos


def main():
    """Entry point."""
    parser = argparse.ArgumentParser()
    autofix_lib.add_fixer_args(parser)
    args = parser.parse_args(None)

    repos, cfg, commit, stg = autofix_lib.from_cli(
        args,
        find_repos=find_repos,
        msg=GIT_COMMIT_MSG,
        branch_name=GIT_BRANCH_NAME,
    )
    autofix_lib.fix(
        repos,
        apply_fix=apply_fix,
        config=cfg,
        commit=commit,
        autofix_settings=stg,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
