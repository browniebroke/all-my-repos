from __future__ import annotations

import argparse
import json
from pathlib import Path

from all_repos import autofix_lib
from all_repos.grep import repos_matching

# Find repos that have this file...
FILE_NAMES = [".github/workflows"]
# ... and which content contains this string.
FILE_CONTAINS = "browniebroke/github-actions/.github/workflows/ts-lint.yml"
# Git stuff
GIT_COMMIT_MSG = "chore: migrate from ESLint & Prettier to Oxlint & Oxfmt"
GIT_BRANCH_NAME = "chore/oxlint-oxfmt"

# Oxfmt doesn't support Prettier plugins, e.g. Astro files would stop being formatted
UNSUPPORTED_PRETTIER_PLUGINS = ["prettier-plugin-astro", "prettier-plugin-svelte"]

OLD_DEV_DEPS = [
    "@eslint/compat",
    "@eslint/eslintrc",
    "@eslint/js",
    "@typescript-eslint/parser",
    "eslint",
    "eslint-config-next",
    "eslint-config-prettier",
    "eslint-plugin-prettier",
    "eslint-plugin-react",
    "globals",
    "prettier",
]
NEW_DEV_DEPS = ["oxlint", "oxfmt"]

SCRIPTS = {
    "format": "oxfmt",
    "check:lint": "oxlint",
    "check:format": "oxfmt --check",
}

DOCS_REPLACEMENTS = {
    "Run ESLint": "Run Oxlint",
    "Check Prettier formatting": "Check Oxfmt formatting",
    "Auto-format with Prettier": "Auto-format with Oxfmt",
    "enforced by Prettier": "enforced by Oxfmt",
    "ESLint flat config (`eslint.config.mjs`) with Prettier integration": (
        "Oxlint config (`.oxlintrc.json`) and Oxfmt config (`.oxfmtrc.json`)"
    ),
}


def _should_fix_repo(repo: Path) -> bool:
    """
    Do further filtering on each repo.

    Return:
    - True for repos where the fix should run
    - False for repos where the fix should be skipped
    """
    package_json = (repo / "package.json").read_text()
    if any(plugin in package_json for plugin in UNSUPPORTED_PRETTIER_PLUGINS):
        return False
    return (repo / "eslint.config.mjs").exists()


def apply_fix():
    """
    Apply fix to a matching repo.

    To run a command in the context of the repo, use autofix_lib.run. For example:

        autofix_lib.run("uv", "sync")
    """
    package_json = json.loads(Path("package.json").read_text())
    all_deps = {
        **package_json.get("dependencies", {}),
        **package_json.get("devDependencies", {}),
    }
    autofix_lib.run("npm", "ci")

    # Formatter: convert Prettier config (package.json key + .prettierignore)
    autofix_lib.run("npx", "--yes", "oxfmt@latest", "--migrate=prettier")
    autofix_lib.run("npm", "pkg", "delete", "prettier")
    Path(".prettierignore").unlink(missing_ok=True)
    Path(".prettierrc").unlink(missing_ok=True)

    # Linter: lean config, .gitignore is respected by default
    oxfmt_config = json.loads(Path(".oxfmtrc.json").read_text())
    plugins = ["typescript", "unicorn", "oxc"]
    if "react" in all_deps:
        plugins += ["react", "jsx-a11y"]
    ignore_patterns = list(oxfmt_config.get("ignorePatterns", []))
    if "next" in all_deps:
        plugins += ["import", "nextjs"]
        ignore_patterns.append("next-env.d.ts")
    oxlint_config = {
        "$schema": "./node_modules/oxlint/configuration_schema.json",
        "plugins": plugins,
        "categories": {"correctness": "error"},
        "env": {"browser": True, "node": True},
        "ignorePatterns": ignore_patterns,
    }
    Path(".oxlintrc.json").write_text(json.dumps(oxlint_config, indent=2) + "\n")
    Path("eslint.config.mjs").unlink(missing_ok=True)

    # Dependencies & scripts
    to_remove = [dep for dep in OLD_DEV_DEPS if dep in all_deps]
    autofix_lib.run("npm", "uninstall", *to_remove)
    autofix_lib.run("npm", "install", "--save-dev", "--save-exact", *NEW_DEV_DEPS)
    for name, command in SCRIPTS.items():
        autofix_lib.run("npm", "pkg", "set", f"scripts.{name}={command}")

    # Docs
    for doc in [Path("CLAUDE.md"), Path("AGENTS.md"), Path("README.md")]:
        if not doc.exists():
            continue
        content = doc.read_text()
        for old, new in DOCS_REPLACEMENTS.items():
            content = content.replace(old, new)
        doc.write_text(content)

    # Format with the new tool & ensure formatting is stable
    autofix_lib.run("npm", "run", "format")
    autofix_lib.run("npm", "run", "check:format")
    # Oxlint enables more rules than the old ESLint setups (which only ran Prettier),
    # fix what can be fixed; leftovers are reported by CI on the PR
    autofix_lib.run("npx", "oxlint", "--fix", "--fix-suggestions", check=False)

    # all-repos commits with `git commit -a`, which skips new files
    autofix_lib.run("git", "add", ".oxlintrc.json", ".oxfmtrc.json")


# You shouldn't need to change anything below this line


def find_repos(config) -> set[str]:
    """Find matching repos using git grep."""
    repos = repos_matching(
        config,
        (FILE_CONTAINS, "--", *FILE_NAMES),
    )
    return {repo for repo in repos if _should_fix_repo(Path(repo))}


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
