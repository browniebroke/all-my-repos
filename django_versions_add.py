from __future__ import annotations

import argparse
from pathlib import Path

from all_repos import autofix_lib
from all_repos.grep import repos_matching

# Find repos that have this file...
FILE_NAMES = ["pyproject.toml", "project/pyproject.toml.jinja"]
# ... and which content contains this string.
FILE_CONTAINS = "Framework :: Django"
# Git stuff
GIT_COMMIT_MSG = "feat: add Django 6.1 support"
GIT_BRANCH_NAME = "feat/add-django-6.1"


def apply_fix():
    """Apply fix to a matching repo."""
    pyproj = Path("pyproject.toml")
    if pyproj.exists() and "Framework :: Django :: 6.1" in pyproj.read_text():
        # Idempotent: skip if already applied
        return

    # 1. tox.ini
    tox_ini_paths = [
        Path("tox.ini"),
        Path("project/{% if is_django_package %}tox.ini{% endif %}.jinja"),
    ]
    for tox_ini in tox_ini_paths:
        if not tox_ini.exists():
            continue
        tox_ini_content = tox_ini.read_text()
        tox_ini_replacements = {
            "-django{60,52}": "-django{61,60,52}",
            "    django60: django60": "    django61: django61\n    django60: django60",
        }
        for from_str, to_str in tox_ini_replacements.items():
            tox_ini_content = tox_ini_content.replace(from_str, to_str)
        tox_ini.write_text(tox_ini_content)

    # 2. pyproject.toml
    pyproject_toml_paths = [
        Path("pyproject.toml"),
        Path("project/pyproject.toml.jinja"),
    ]
    for index, pyproject_toml in enumerate(pyproject_toml_paths):
        if not pyproject_toml.exists():
            continue
        pyproject_toml_content = pyproject_toml.read_text()
        pyproject_toml_replacements = {
            '  "Framework :: Django :: 6.0",': '  "Framework :: Django :: 6.0",\n  "Framework :: Django :: 6.1",',
            'django60 = [ "django>=6.0a1,<6.1; python_version>=\'3.12\'" ]': 'django60 = [ "django>=6.0a1,<6.1; python_version>=\'3.12\'" ]\ndjango61 = [ "django>=6.1a1,<6.2; python_version>=\'3.12\'" ]',
            '    { group = "django60" },':'    { group = "django61" },\n    { group = "django60" },',
        }
        for from_str, to_str in pyproject_toml_replacements.items():
            pyproject_toml_content = pyproject_toml_content.replace(from_str, to_str)
        pyproject_toml.write_text(pyproject_toml_content)

        if index == 0:
            autofix_lib.run("uv", "lock")


# You shouldn't need to change anything below this line


def find_repos(config) -> set[str]:
    """Find matching repos using git grep."""
    repos = repos_matching(
        config,
        (FILE_CONTAINS, "--", *FILE_NAMES),
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
