from __future__ import annotations

import argparse
from pathlib import Path

from all_repos import autofix_lib
from all_repos.grep import repos_matching

# Find repos that have this file...
FILE_NAMES = [".github/workflows/ci.yml"]
# ... and which content contains this string.
FILE_CONTAINS = "uses: actions/setup-python"
# Git stuff
GIT_COMMIT_MSG = "ci: remove actions/setup-python in GHA"
GIT_BRANCH_NAME = "ci/remove-actions-steup-python"

CI_BEFORE = """
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7
      - uses: actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97 # v7
        with:
          python-version: ${{ matrix.python-version }}
          allow-prereleases: true
      - uses: astral-sh/setup-uv@c771a70e6277c0a99b617c7a806ffedaca235ff9 # v9.0.0
      - run: uv sync --no-python-downloads"""
CI_AFTER = """
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7
      - uses: astral-sh/setup-uv@c771a70e6277c0a99b617c7a806ffedaca235ff9 # v9.0.0
        with:
          python-version: ${{ matrix.python-version }}
      - run: uv sync"""

LABELS_BEFORE = """
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7
      - name: Set up Python
        uses: actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97 # v7
        with:
          python-version: 3.x
      - name: Install labels
        run: pip install labels
      - name: Sync config with Github
        run: labels -u ${{ github.repository_owner }} -t ${{ secrets.GITHUB_TOKEN }} sync -f .github/labels.toml"""
LABELS_AFTER = """
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7
      - uses: astral-sh/setup-uv@c771a70e6277c0a99b617c7a806ffedaca235ff9 # v9.0.0
      - name: Sync config with Github
        run: uvx labels -u ${{ github.repository_owner }} -t ${{ secrets.GH_PAT }} sync -f .github/labels.toml"""


def apply_fix():
    """
    Apply fix to a matching repo.

    To run a command in the context of the repo, use autofix_lib.run. For example:

        autofix_lib.run("uv", "sync")
    """
    # ci.yml
    file_paths = [
        Path(".github/workflows/ci.yml"),
        Path("project/.github/workflows/ci.yml.jinja"),
    ]
    for ci_yaml in file_paths:
        if not ci_yaml.exists():
            continue
        content = ci_yaml.read_text()
        if "actions/setup-python" not in content:
            continue

        content = content.replace(CI_BEFORE, CI_AFTER)
        ci_yaml.write_text(content)

    # labels.yml
    file_paths = [
        Path(".github/workflows/labels.yml"),
        Path("project/.github/workflows/labels.yml"),
    ]
    for labels_yml in file_paths:
        if not labels_yml.exists():
            continue

        content = labels_yml.read_text()
        if "actions/setup-python" not in content:
            continue

        content = content.replace(LABELS_BEFORE, LABELS_AFTER)
        labels_yml.write_text(content)


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
