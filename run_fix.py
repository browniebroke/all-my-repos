from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import tomli
from all_repos import autofix_lib
from all_repos.grep import repos_matching


def find_repos(config) -> set[str]:
    repos = repos_matching(
        config, ("github>browniebroke/renovate-configs:js-app", "--", "package.json")
    )
    print(repos)
    return repos


def apply_fix():
    if "nwtgck/actions-netlify" in Path(".github/workflows/ci.yml").read_text():
        return
    package_json_path = Path("package.json")
    content = package_json_path.read_text()
    package_json_config = json.loads(content)
    package_json_config["renovate"]["extends"].append(
        "github>browniebroke/renovate-configs:netlify"
    )
    updated_content = json.dumps(package_json_config, indent=2, ensure_ascii=False)
    package_json_path.write_text(f"{updated_content}\n")
    autofix_lib.run("/usr/local/bin/prettier", "--write", "package.json")


def main(argv=None):
    parser = argparse.ArgumentParser()
    autofix_lib.add_fixer_args(parser)
    args = parser.parse_args(argv)

    repos, config, commit, autofix_settings = autofix_lib.from_cli(
        args,
        find_repos=find_repos,
        msg="chore: update renovate config",
        branch_name="chore/update-renovate",
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
