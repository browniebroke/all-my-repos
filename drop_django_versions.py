from __future__ import annotations

import argparse
from pathlib import Path

from all_repos import autofix_lib
from all_repos.grep import repos_matching

# Find repos that have this file...
FILE_NAME = "tox.ini"
# ... and which content contains this string.
FILE_CONTAINS = "django32"
# Git stuff
GIT_COMMIT_MSG = (
    "feat: drop Django < 4.2 support\n\n"
    "BREAKING CHANGE: drop support for Django < 4.2\n"
)
GIT_BRANCH_NAME = "feat/drop-django-lt-42"


def apply_fix():
    """Apply fix to a matching repo."""
    # 1. tox.ini
    tox_ini = Path("tox.ini")
    tox_ini_content = tox_ini.read_text()
    tox_ini_replacements = {
        "django{50,42,41}": "django{50,42}",
        "django{50,42,41,40}": "django{50,42}",
        "django{50,42,41,40,32}": "django{50,42}",
        "django{42,41,40,32}": "django{42}",
        "    django41: Django>=4.1,<4.2\n": "",
        "    django40: Django>=4.0,<4.1\n": "",
        "    django32: Django>=3.2,<4.0\n": "",
    }
    for from_str, to_str in tox_ini_replacements.items():
        tox_ini_content = tox_ini_content.replace(from_str, to_str)
    tox_ini.write_text(tox_ini_content)

    # 2. pyproject.toml
    pyproject_toml = Path("pyproject.toml")
    pyproject_toml_content = pyproject_toml.read_text()
    pyproject_toml_replacements = {
        '    "Framework :: Django :: 3.2",\n': "",
        '    "Framework :: Django :: 4.0",\n': "",
        '    "Framework :: Django :: 4.1",\n': "",
        'django = ">=3.2"': 'django = ">=4.2"',
    }
    for from_str, to_str in pyproject_toml_replacements.items():
        pyproject_toml_content = pyproject_toml_content.replace(from_str, to_str)
    pyproject_toml.write_text(pyproject_toml_content)
    autofix_lib.run("poetry", "lock", "--no-update")


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
