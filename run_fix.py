from __future__ import annotations

import argparse
from pathlib import Path

from all_repos import autofix_lib
from all_repos.grep import repos_matching

# Find repos that have this file...
FILE_NAMES = [".pre-commit-config.yaml"]
# ... and which content contains this string.
FILE_CONTAINS = "pre-commit/mirrors-mypy"
# Git stuff
GIT_COMMIT_MSG = "chore: migrate from mypy to ty"
GIT_BRANCH_NAME = "chore/mypy-to-ty"


PRE_COMMIT_TY = """
  - repo: local
    hooks:
      - id: local-ty
        name: ty check
        entry: uv run ty check
        require_serial: true
        language: system
        pass_filenames: false
"""

PYPROJECT_CONFIG = """[tool.ty]
terminal.error-on-warning = true

""".splitlines()


def apply_fix():
    """Apply fix to a matching repo."""
    # Update pre-commit config
    pre_commit_config = Path(".pre-commit-config.yaml")
    if pre_commit_config.exists():
        file_content = pre_commit_config.read_text()
        mypy_repo = False
        updated_lines = []
        for line in file_content.splitlines():
            if "pre-commit/mirrors-mypy" in line:
                mypy_repo = True
                continue
            if mypy_repo and line.startswith("  - repo: "):
                mypy_repo = False
            if not mypy_repo:
                updated_lines.append(line)
                continue
        updated_content = "\n".join(updated_lines)
        updated_content += PRE_COMMIT_TY
        pre_commit_config.write_text(updated_content)

    # Update pyproject.toml
    pyproject_toml = Path("pyproject.toml")
    file_content = pyproject_toml.read_text()
    if "[tool.mypy]" in file_content:
        updated_lines = []
        mypy_section = False
        for line in file_content.splitlines():
            if line == "[tool.mypy]":
                mypy_section = True
                updated_lines.extend(PYPROJECT_CONFIG)
                continue
            if mypy_section and line.startswith("[tool."):
                mypy_section = False
            if not mypy_section:
                updated_lines.append(line)
                continue

        pyproject_toml.write_text("\n".join(updated_lines) + "\n")

    # Install ty
    autofix_lib.run("uv", "add", "ty==0.0.31", "--dev")

    # Remove GitPod config
    gitpod_yml = Path(".gitpod.yml")
    if gitpod_yml.exists():
        gitpod_yml.unlink(missing_ok=True)



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
