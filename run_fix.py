from __future__ import annotations

import argparse
from pathlib import Path

from all_repos import autofix_lib
from all_repos.grep import repos_matching


def find_repos(config) -> set[str]:
    repos = repos_matching(
        config,
        (
            "poetry",
            "--",
            "pyproject.toml",
        ),
    )
    print(repos)
    return repos


def apply_fix():
    file_path = Path("pyproject.toml")
    content = file_path.read_text()

    if 'python = "^3.8"' in content:
        return

    content = content.replace('python = "^3.7"', 'python = "^3.8"')
    file_path.write_text(content)

    ci_yml = Path(".github/workflows/ci.yml")
    if ci_yml.exists():
        content = ci_yml.read_text()
        content = content.replace('python-version:\n          - "3.7"\n', 'python-version:\n')
        ci_yml.write_text(content)

    pc_yml = Path(".pre-commit-config.yaml")
    if pc_yml.exists():
        content = pc_yml.read_text()
        content = content.replace('--py37-plus', '--py38-plus')
        pc_yml.write_text(content)

    template_path = Path("project")
    if template_path.exists():
        file_path = template_path / "pyproject.toml.jinja"
        content = file_path.read_text()
        content = content.replace('python = "^3.7"', 'python = "^3.8"')
        file_path.write_text(content)

        ci_yml = template_path / ".github" / "workflows" / "ci.yml"
        content = ci_yml.read_text()
        content = content.replace('python-version:\n          - "3.7"\n', 'python-version:\n')
        ci_yml.write_text(content)

        pc_yml = template_path / ".pre-commit-config.yaml"
        content = pc_yml.read_text()
        content = content.replace('--py37-plus', '--py38-plus')
        pc_yml.write_text(content)

        readme = template_path / "README.md"
        content = readme.read_text()
        content = content.replace('Python 3.7+.', 'Python 3.8+.')
        readme.write_text(content)


def main(argv=None):
    parser = argparse.ArgumentParser()
    autofix_lib.add_fixer_args(parser)
    args = parser.parse_args(argv)

    repos, config, commit, autofix_settings = autofix_lib.from_cli(
        args,
        find_repos=find_repos,
        msg=(
            "feat: drop support for Python 3.7\n\n"
            "BREAKING CHANGE: Drop support for Python 3.7 as it reached EOL on June 27, 2023. "
            "More infos: https://devguide.python.org/versions/"
        ),
        branch_name=f"feat/drop-python-3.7",
    )
    autofix_lib.fix(
        repos,
        apply_fix=apply_fix,
        config=config,
        commit=commit,
        autofix_settings=autofix_settings,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
