from __future__ import annotations

import argparse
from pathlib import Path

from all_repos import autofix_lib
from all_repos.grep import repos_matching

# Find repos that have this file...
FILE_NAMES = ["pyproject.toml", "project/pyproject.toml.jinja"]
# ... and which content contains this string.
FILE_CONTAINS = 'requires-python = ">=3.10"'
# Git stuff
NEW_VERSION = "3.15"
PREV_VERSION = "3.14"
NEW_VERSION_NO_DOT = NEW_VERSION.replace(".", "")
GIT_COMMIT_MSG = (
    f"feat: add support for Python {NEW_VERSION}"
)
GIT_BRANCH_NAME = f"feat/add-python-{NEW_VERSION}"


def apply_fix():
    """Apply fix to a matching repo."""
    # 1. tox.ini
    tox_ini_paths = [
        Path("tox.ini"),
        Path("project/{% if is_django_package %}tox.ini{% endif %}.jinja"),
    ]
    for tox_ini in tox_ini_paths:
        if not tox_ini.exists():
            continue
        tox_ini_content = tox_ini.read_text()
        if f"py{NEW_VERSION_NO_DOT}" in tox_ini_content:
            continue
        tox_ini_replacements = {
            "env_list =\n": f"env_list =\n    py{NEW_VERSION_NO_DOT}-django{{61}}\n",
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
        if f'Programming Language :: Python :: {NEW_VERSION}' in pyproject_toml_content:
            continue

        pyproject_replacements = {
            f'  "Programming Language :: Python :: {PREV_VERSION}",\n': f'  "Programming Language :: Python :: {PREV_VERSION}",\n  "Programming Language :: Python :: {NEW_VERSION}",\n',
            f'max_supported_python = "{PREV_VERSION}"': f'max_supported_python = "{NEW_VERSION}"',
        }

        for from_str, to_str in pyproject_replacements.items():
            pyproject_toml_content = pyproject_toml_content.replace(
                from_str, to_str
            )
        pyproject_toml.write_text(pyproject_toml_content)

    # 3. ci.yml
    ci_yml_paths = [
        Path(".github/workflows/ci.yml"),
        Path("project/.github/workflows/ci.yml.jinja"),
    ]
    for ci_yml in ci_yml_paths:
        if not ci_yml.exists():
            continue
        ci_yml_content = ci_yml.read_text()
        if f'- "{NEW_VERSION}"' in ci_yml_content:
            continue
        ci_yml_content = ci_yml_content.replace(
            f'          - "{PREV_VERSION}"\n',
            f'          - "{PREV_VERSION}"\n          - "{NEW_VERSION}"\n',
        )
        ci_yml.write_text(ci_yml_content)


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
