from __future__ import annotations
import argparse
from pathlib import Path

from all_repos import autofix_lib
from all_repos.grep import repos_matching


def find_repos(config) -> set[str]:
    repos = repos_matching(config, ("jobs:", "--", ".github/workflows/ci.yml"))
    return repos


def apply_fix():
    ci_path = Path(".github/workflows/ci.yml")
    content = ci_path.read_text()
    if "concurrency:" in content:
        return
    content = content.replace(
        "jobs:",
        "\n".join(
            [
                "concurrency:",
                "  group: ${{ github.head_ref || github.run_id }}",
                "  cancel-in-progress: true",
                "",
                "jobs:",
            ]
        ),
    )
    ci_path.write_text(content)


def main(argv=None):
    parser = argparse.ArgumentParser()
    autofix_lib.add_fixer_args(parser)
    args = parser.parse_args(argv)

    repos, config, commit, autofix_settings = autofix_lib.from_cli(
        args,
        find_repos=find_repos,
        msg="ci: avoid concurrent CI runs",
        branch_name="concurrent-ci",
    )
    print(repos)
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
