from __future__ import annotations

import argparse
from pathlib import Path

from all_repos import autofix_lib
from all_repos.grep import repos_matching

# Find repos that have this file...
FILE_NAMES = [
    ".github/workflows/ci.yml",
    "project/.github/workflows/ci.yml.jinja"
]
# ... and which content contains this string.
FILE_CONTAINS = 'pypa/gh-action-pypi-publish@release'
# Git stuff
GIT_COMMIT_MSG = "chore: attest build provenance"
GIT_BRANCH_NAME = "chore/attest-provenance"

NEW_CONTENT = """      - name: Attest build provenance
        uses: actions/attest-build-provenance@v1
        if: steps.release.outputs.released == 'true'
        with:
          subject-path: "dist/*"

"""


def apply_fix():
    """Apply fix to a matching repo."""
    # ci.yml
    print("starting new repo")
    for file_name in FILE_NAMES:
        file_path = Path(file_name)
        if not file_path.exists():
            continue

        content = file_path.read_text()
        if "actions/attest-build-provenance" in content:
            continue

        content = content.replace(
            "      - name: Publish package distributions to PyPI",
            f"{NEW_CONTENT}      - name: Publish package distributions to PyPI"
        )
        content = content.replace(
            "      id-token: write",
            "      id-token: write\n      attestations: write"
        )
        file_path.write_text(content)


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
