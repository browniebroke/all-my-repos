from __future__ import annotations

import argparse
from pathlib import Path

from all_repos import autofix_lib
from all_repos.grep import repos_matching

# Find repos that have this file...
FILE_NAME = "pyproject.toml"
# ... and which content contains this string.
FILE_CONTAINS = "[tool.semantic_release]"
# Git stuff
GIT_COMMIT_MSG = "chore: add code of conduct"
GIT_BRANCH_NAME = "chore/coc"


def apply_fix():
    """Apply fix to a matching repo."""
    coc_content = (Path(__file__).parent / "CODE_OF_CONDUCT.md").read_text()
    dot_github = Path(".github")
    if not dot_github.exists():
        return

    file_path = dot_github / "CODE_OF_CONDUCT.md"
    file_path.write_text(coc_content)

    autofix_lib.run("git", "add", str(file_path))

    root_coc = Path("CODE_OF_CONDUCT.md")
    root_coc.unlink(missing_ok=True)


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
