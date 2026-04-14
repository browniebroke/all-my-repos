from __future__ import annotations

import argparse
from pathlib import Path

from all_repos import autofix_lib
from all_repos.grep import repos_matching

# Find repos that have this file...
FILE_NAMES = [".pre-commit-config.yaml"]
# ... and which content contains this string.
FILE_CONTAINS = "pre-commit.ci"
# Git stuff
GIT_COMMIT_MSG = "ci: migrate from pre-commit to prek"
GIT_BRANCH_NAME = "ci/pre-commmit-to-prek"

JOB_TO_ADD = """  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6.0.2
      - uses: astral-sh/setup-uv@v8.0.0
      - uses: j178/prek-action@v2.0.2
"""


def apply_fix():
    """Apply fix to a matching repo."""
    ci_yml = Path(".github/workflows/ci.yml")
    if ci_yml.exists():
        file_content = ci_yml.read_text()
        if "j178/prek-action" not in file_content:
            updated_lines = []
            for line in file_content.splitlines():
                updated_lines.append(line)
                if line == "jobs:":
                    updated_lines.extend(JOB_TO_ADD.splitlines())
                    updated_lines.append("")
            file_content = "\n".join(updated_lines) + "\n"
            file_content = file_content.replace(
                "    needs:\n"
                "      - test",
                "    needs:\n"
                "      - lint\n"
                "      - test"
            )
            ci_yml.write_text(file_content)

    contributing_md = Path("CONTRIBUTING.md")
    if contributing_md.exists():
        file_content = contributing_md.read_text()
        if "https://prek.j178.dev/" not in file_content:
            file_content = file_content.replace(
                "[pre-commit](https://pre-commit.com)",
                "[prek](https://prek.j178.dev/)",
            )
            file_content = file_content.replace("pre-commit", "prek")
            file_content = file_content.replace("prek install", "prek install -f")
            contributing_md.write_text(file_content)

    readme_md = Path("README.md")
    if readme_md.exists():
        file_content = readme_md.read_text()
        file_content = file_content.replace(
            '<a href="https://github.com/pre-commit/pre-commit">',
            '<a href="https://github.com/j178/prek">',
        )
        file_content = file_content.replace(
            '<img src="https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white&style=flat-square" alt="pre-commit">',
            '<img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/j178/prek/master/docs/assets/badge-v0.json" alt="prek">',
        )
        readme_md.write_text(file_content)

    gitpod_yaml = Path(".gitpod.yaml")
    if gitpod_yaml.exists():
        file_content = gitpod_yaml.read_text()
        file_content = file_content.replace(
            "      pip install pre-commit\n"
            "      pre-commit install\n"
            "      PIP_USER=false pre-commit install-hooks",
            "      pip install prek\n"
            "      prek install -f"
        )
        gitpod_yaml.write_text(file_content)

    pr_template_md = Path(".github/PULL_REQUEST_TEMPLATE.md")
    if pr_template_md.exists():
        file_content = pr_template_md.read_text()
        file_content = file_content.replace(
            '> - If pre-commit.ci is failing, try `pre-commit run -a` for further information.',
            '> - If the lint job is failing, try `prek run -a` for further information.',
        )
        pr_template_md.write_text(file_content)


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
