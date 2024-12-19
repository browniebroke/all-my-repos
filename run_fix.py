from __future__ import annotations

import argparse
from pathlib import Path

from all_repos import autofix_lib
from all_repos.grep import repos_matching

# Find repos that have this file...
FILE_NAMES = [
    "poetry.lock",
]
# ... and which content contains this string.
FILE_CONTAINS = "content-hash"
# Git stuff
GIT_COMMIT_MSG = "chore: migrate migrate packaging to uv"
GIT_BRANCH_NAME = "packaging/migrate-to-uv"


def apply_fix():
    """Apply fix to a matching repo."""
    autofix_lib.run("pdm", "import", "-f", "poetry", "pyproject.toml")

    # 1. pyproject.toml
    pyproject_toml = Path("pyproject.toml")
    content = pyproject_toml.read_text()

    inside_poetry_table = False
    inside_build_system_table = False
    inside_pdm_build_table = False
    new_lines = []

    for line in content.splitlines():
        if line.startswith("[tool.poetry"):
            inside_poetry_table = True
        elif line.startswith("[") and inside_poetry_table:
            inside_poetry_table = False
        if inside_poetry_table:
            continue

        if line == "[build-system]":
            inside_build_system_table = True
        elif line.startswith("[") and inside_build_system_table:
            inside_build_system_table = False
        if inside_build_system_table:
            continue

        if line == "[tool.pdm.build]":
            inside_pdm_build_table = True
        elif line.startswith("[") and inside_pdm_build_table:
            inside_pdm_build_table = False
        if inside_pdm_build_table:
            continue

        if line == "[tool.pdm.dev-dependencies]":
            new_lines.append("[dependency-groups]")
            continue

        if line == 'version_toml = [ "pyproject.toml:tool.poetry.version" ]':
            new_lines.append('version_toml = [ "pyproject.toml:project.version" ]')
            continue

        if line == 'build_command = "pip install poetry && poetry build"':
            new_lines.extend([
                'build_command = """',
                'pip install uv',
                'uv lock',
                'git add uv.lock',
                'uv build',
                '"""',
            ])
            continue

        if line == 'requires-python = "<4.0,>=3.9"':
            new_lines.append('requires-python = ">=3.9"')
            continue

        new_lines.append(line)

    pyproject_toml.write_text("\n".join(new_lines))

    # 2. poetry.lock -> uv.lock
    autofix_lib.run("rm", "poetry.lock")
    autofix_lib.run("uv", "lock")
    autofix_lib.run("git", "add", "uv.lock")

    # 3. pre-commit config
    pre_commit_config = Path(".pre-commit-config.yaml")
    if pre_commit_config.exists():
        content = pre_commit_config.read_text()
        new_content = content.replace("""  - repo: https://github.com/python-poetry/poetry
    rev: 1.8.5
    hooks:
      - id: poetry-check""", """  - repo: https://github.com/astral-sh/uv-pre-commit
    rev: 0.5.10
    hooks:
      - id: uv-lock""")
        new_content = new_content.replace(
            "default_stages: [commit]",
            "default_stages: [pre-commit]",
        )
        pre_commit_config.write_text(new_content)

    # 4. gitpod config
    gitpod_config = Path(".gitpod.yml")
    if gitpod_config.exists():
        new_content = (
            gitpod_config.read_text()
            .replace("pip install poetry","pip install uv")
            .replace("poetry install","uv sync")
        )
        gitpod_config.write_text(new_content)

    # 5. Upgrader workflow
    upgrader_yml = Path(".github/workflows/poetry-upgrade.yml")
    if upgrader_yml.exists():
        content = upgrader_yml.read_text()
        new_content = content.replace(
            "browniebroke/github-actions/.github/workflows/poetry-upgrade.yml@v1",
            "browniebroke/github-actions/.github/workflows/uv-upgrade.yml@v1",
        )
        upgrader_yml.unlink()
        upgrader_yml = Path(".github/workflows/upgrader.yml")
        upgrader_yml.write_text(new_content)
        autofix_lib.run("git", "add", str(upgrader_yml))

    # 6. Contributing guide
    contributing_md = Path("CONTRIBUTING.md")
    if contributing_md.exists():
        new_content = (
            contributing_md
            .read_text()
            .replace("[Poetry](https://python-poetry.org)", "[uv](https://docs.astral.sh/uv/)")
            .replace("poetry install", "uv sync")
            .replace("poetry run pytest", "uv run pytest")
        )
        contributing_md.write_text(new_content)

    # 7. README
    readme_md = Path("README.md")
    if readme_md.exists():
        new_content = (
            readme_md
            .read_text()
            .replace("https://python-poetry.org/", "https://github.com/astral-sh/uv")
            .replace("https://python-poetry.org/badge/v0.json", "https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json")
            .replace('alt="Poetry"', 'alt="uv"')
        )
        readme_md.write_text(new_content)

    # CI Workflow
    ci_yml = Path(".github/workflows/ci.yml")
    if ci_yml.exists():
        new_content = (
            ci_yml
            .read_text()
            .replace(
                # from
                "      - name: Install poetry\n"
                "        run: pipx install poetry\n",
                # to
                "",
            )
            .replace(
                # from
                "      - run: pipx install poetry\n",
                # to
                "",
            )
            .replace(
                # from
                "      - name: Set up Python\n"
                "        uses: actions/setup-python@v5",
                # to
                "      - uses: actions/setup-python@v5",
            )
            .replace(
                "          cache: poetry\n",
                "",
            )
            .replace(
                # from
                "      - name: Install Dependencies\n"
                "        run: poetry install\n",
                # to
                '      - uses: astral-sh/setup-uv@v4\n'
                '        with:\n'
                '          enable-cache: "true"\n'
                '      - run: uv sync --no-python-downloads\n'
            )
            .replace(
                # from
                "      - run: poetry install\n",
                # to
                '      - uses: astral-sh/setup-uv@v4\n'
                '        with:\n'
                '          enable-cache: "true"\n'
                '      - run: uv sync --no-python-downloads\n'
            )
            .replace(
                # from
                "      - name: Test with Pytest\n"
                "        run: poetry run pytest --cov-report=xml",
                # to
                "      - run: uv run pytest --cov-report=xml",
            )
            .replace(
                # from
                "      - run: poetry run pytest --cov-report=xml",
                # to
                "      - run: uv run pytest --cov-report=xml",
            )
            .replace(
                # from
                "      - name: Upload coverage to Codecov\n"
                "        uses: codecov/codecov-action@v4",
                # to
                "      - uses: codecov/codecov-action@v4",
            )
        )
        ci_yml.write_text(new_content)

    print("Done with repo")


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
