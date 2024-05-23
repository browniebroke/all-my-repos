from __future__ import annotations

import argparse
from pathlib import Path

from all_repos import autofix_lib
from all_repos.grep import repos_matching

# Find repos that have this file...
FILE_NAME = ".pre-commit-config.yaml"
# ... and which content contains this string.
FILE_CONTAINS = "https://github.com/psf/black"
# Git stuff
GIT_COMMIT_MSG = "chore: switch to Ruff formatter"
GIT_BRANCH_NAME = "chore/ruff-formatter"


def apply_fix():
    """Apply fix to a matching repo."""
    breakpoint()
    file_paths = [
        Path(FILE_NAME),
        Path("project") / FILE_NAME,
    ]
    for file_path in file_paths:
        if not file_path.exists():
            continue

        file_content = file_path.read_text()
        if "- id: ruff-format" in file_content:
            continue

        updated_lines = []
        inside_ruff = False
        inside_black = False
        for line in file_content.splitlines():
            if inside_ruff and line.startswith("  - repo: "):
                updated_lines.append("      - id: ruff-format")
                inside_ruff = False

            if "https://github.com/astral-sh/ruff-pre-commit" in line:
                inside_ruff = True

            if inside_black:
                if line.startswith("  - repo: "):
                    inside_black = False
                else:
                    continue

            if "repo: https://github.com/psf/black" in line:
                inside_black = True
                continue

            updated_lines.append(line)

        # Add newline at end of file
        updated_lines.append("")
        file_path.write_text("\n".join(updated_lines))

    readme_paths = [
        Path("README.md"),
        Path("project") / "README.md",
    ]
    for readme_path in readme_paths:
        if not readme_path.exists():
            continue

        readme_content = readme_path.read_text()
        readme_content = readme_content.replace(
            "https://github.com/ambv/black",
            "https://github.com/astral-sh/ruff",
        )
        readme_content = readme_content.replace(
            'src="https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square" alt="black"',
            'src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff"',
        )
        readme_path.write_text(readme_content)



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
