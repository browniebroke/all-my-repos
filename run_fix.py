from __future__ import annotations

import argparse
import re
from pathlib import Path

import tomli
from all_repos import autofix_lib
from all_repos.grep import repos_matching


def find_repos(config) -> set[str]:
    repos = repos_matching(config, ("=", "--", "poetry.lock"))
    print(repos)
    return repos


def apply_fix():
    pyproject_toml = Path("pyproject.toml")
    content = pyproject_toml.read_text()
    pyproject_config = tomli.loads(content)
    deps = pyproject_config["tool"]["poetry"]["dependencies"]
    dev_deps = pyproject_config["tool"]["poetry"]["dev-dependencies"]
    all_deps = {**deps, **dev_deps}
    for package, version_spec in all_deps.items():
        if package == "python":
            continue
        if isinstance(version_spec, dict):
            version = version_spec['version']
            digits = version.split(".")
            if digits[0].lstrip("^>=<") > "0" and len(digits) > 2:
                # patch specified for non zero-ver package
                updated_version = ".".join(digits[:2])
                content = content.replace(
                    ' = {version =',
                    ' = { version =',
                )
                content = content.replace(
                    'optional = true}',
                    'optional = true }',
                )
                content = content.replace(
                    package + ' = { version = "' + version + '"',
                    package + ' = { version = "' + updated_version + '"',
                )
        else:
            digits = version_spec.split(".")
            if digits[0].lstrip("^>=<") > "0" and len(digits) > 2:
                # patch specified for non zero-ver package
                updated_version = ".".join(digits[:2])
                content = content.replace(
                    f'{package} = "{version_spec}"',
                    f'{package} = "{updated_version}"',
                )
    pyproject_toml.write_text(content)
    autofix_lib.run("poetry", "lock", "--no-update")


def main(argv=None):
    parser = argparse.ArgumentParser()
    autofix_lib.add_fixer_args(parser)
    args = parser.parse_args(argv)

    repos, config, commit, autofix_settings = autofix_lib.from_cli(
        args,
        find_repos=find_repos,
        msg="chore: drop patch version for all stable dependencies",
        branch_name="drop-patch",
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
