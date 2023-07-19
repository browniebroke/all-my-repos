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
GIT_COMMIT_MSG = "chore: customise PSR v8 changelog generation"
GIT_BRANCH_NAME = "chore/psr-v8-changelog"

PYPROJECT_TOML_DIFF = """[tool.semantic_release.changelog]
exclude_commit_patterns = [
    "chore*",
    "ci*",
]

[tool.semantic_release.changelog.environment]
keep_trailing_newline = true

"""

CHANGELOG_TEMPLATE = """# CHANGELOG

{%- for version, release in context.history.released.items() %}
{%- if version.as_tag() > "v1.0.0" %}

## {{ version.as_tag() }} ({{ release.tagged_date.strftime("%Y-%m-%d") }})

{%- for category, commits in release["elements"].items() %}
{# Category title: Breaking, Fix, Documentation #}
### {{ category | capitalize }}
{# List actual changes in the category #}
{%- for commit in commits %}
- {{ commit.descriptions[0] | capitalize }} ([`{{ commit.short_hash }}`]({{ commit.hexsha | commit_hash_url }}))
{%- endfor %}{# for commit #}

{%- endfor %}{# for category, commits #}

{%- endif %}{# if version.as_tag() #}

{%- endfor %}{# for version, release #}

{% include ".changelog-old.md" %}{# include old changelog at the end -#}
"""


def apply_fix():
    """Apply fix to a matching repo."""
    pyproject_toml = Path("pyproject.toml")
    content = pyproject_toml.read_text()
    if "[tool.semantic_release.changelog]" in content:
        # Already updated
        return

    changelog_file = Path("CHANGELOG.md")
    if not changelog_file.exists():
        # No changelog file
        return

    # read until end of [tool.semantic_release] section
    updated_lines = []
    inside_section = False
    section_passed = False
    inserted = False
    for line in content.splitlines():
        updated_lines.append(line)
        if line == "[tool.semantic_release]":
            inside_section = True
        if inside_section and line == "":
            inside_section = False
            section_passed = True
        if section_passed and not inserted:
            updated_lines.extend(PYPROJECT_TOML_DIFF.splitlines())
            inserted = True

    # write back content
    new_content = "\n".join(updated_lines)
    pyproject_toml.write_text(new_content)

    # Create template dir
    templates_dir = Path("templates")
    templates_dir.mkdir()

    # Create changelog template & save old changelog
    (templates_dir / "CHANGELOG.md.j2").write_text(CHANGELOG_TEMPLATE)
    old_changelog_content = changelog_file.read_text()
    old_changelog_content = old_changelog_content.replace(
        "# Changelog",
        "",
    )
    old_changelog_content = old_changelog_content.replace(
        "<!--next-version-placeholder-->",
        "",
    )
    old_changelog_content = old_changelog_content.lstrip("\n")
    (templates_dir / ".changelog-old.md").write_text(old_changelog_content)
    autofix_lib.run("git", "add", ".")
    breakpoint()


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
