"""Release helper — bumps version, updates CHANGELOG, commits and tags.

Usage:
    python scripts/release.py patch   # 0.1.0 -> 0.1.1
    python scripts/release.py minor   # 0.1.0 -> 0.2.0
    python scripts/release.py major   # 0.1.0 -> 1.0.0

The bump type only controls the version number.

Release notes are read from the `Entries` section in docs/unreleased_changelog.md
as a flat list.

Each line should use this format:
  - [package] message
  - [package][changed] message
  - [package][fixed] message
  - [package][removed] message

If the change tag is omitted, the entry is treated as Added.
The script groups the final release notes by category and package.

After a release, the unreleased file is reset to the empty template.
"""

import re
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT         = Path(__file__).parent.parent
PYPROJECT    = ROOT / "pyproject.toml"
CHANGELOG    = ROOT / "docs" / "CHANGELOG.md"
UNRELEASED   = ROOT / "docs" / "unreleased_changelog.md"

CHANGELOG_HEADER = """\
# Changelog

All notable changes to TinyUI are documented here.
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

"""

VALID_BUMPS = {"patch", "minor", "major"}
CHANGELOG_CATEGORIES = ("Added", "Changed", "Fixed", "Removed")
PACKAGE_ORDER = ("app", "plugins", "tinycore", "tinyui", "tinywidgets", "other")

UNRELEASED_TEMPLATE = """\
# Unreleased

Add entries here before running a release.
The release script controls the version bump, category, and grouping.

## Format

Use one line per change:
  - [tinycore] New provider registry API
  - [tinyui][fixed] Settings panel not opening from toolbar
  - [tinywidgets][removed] Legacy overlay shim
  - [plugins][changed] LMU connector now logs session transitions

Known packages:
  - app
  - plugins
  - tinycore
  - tinyui
  - tinywidgets
  - other

## Entries
"""


# ── Version helpers ───────────────────────────────────────────────────────────

def _read_version() -> tuple[int, int, int]:
    text = PYPROJECT.read_text(encoding="utf-8")
    m = re.search(r'^version\s*=\s*"(\d+)\.(\d+)\.(\d+)"', text, re.MULTILINE)
    if not m:
        raise SystemExit("ERROR: version not found in pyproject.toml")
    return int(m.group(1)), int(m.group(2)), int(m.group(3))


def _bump(version: tuple[int, int, int], bump_type: str) -> tuple[int, int, int]:
    major, minor, patch = version
    if bump_type == "major":
        return major + 1, 0, 0
    if bump_type == "minor":
        return major, minor + 1, 0
    return major, minor, patch + 1


def _write_version(version: tuple[int, int, int]):
    new_ver = "%d.%d.%d" % version
    text = PYPROJECT.read_text(encoding="utf-8")
    text = re.sub(
        r'^(version\s*=\s*)"[\d.]+"',
        f'\\1"{new_ver}"',
        text,
        flags=re.MULTILINE,
    )
    PYPROJECT.write_text(text, encoding="utf-8")
    return new_ver


# ── Changelog helpers ─────────────────────────────────────────────────────────

def _normalize_category(raw: str | None) -> str:
    """Map short change tags to changelog category names."""
    if raw is None:
        return "Added"

    value = raw.strip().lower()
    mapping = {
        "add": "Added",
        "added": "Added",
        "change": "Changed",
        "changed": "Changed",
        "fix": "Fixed",
        "fixed": "Fixed",
        "remove": "Removed",
        "removed": "Removed",
    }
    if value not in mapping:
        raise SystemExit(
            f"Unknown changelog tag '{raw}'. Use added, changed, fixed, or removed."
        )
    return mapping[value]


def _parse_unreleased() -> dict[str, dict[str, list[str]]]:
    """Parse unreleased_changelog.md into category -> package -> entries."""
    text = UNRELEASED.read_text(encoding="utf-8")
    result: dict[str, dict[str, list[str]]] = {
        category: {} for category in CHANGELOG_CATEGORIES
    }
    in_entries = False

    for line in text.splitlines():
        stripped = line.strip()
        if stripped == "## Entries":
            in_entries = True
            continue
        if not in_entries:
            continue
        if not stripped or stripped.startswith("#"):
            continue
        match = re.match(
            r"^-\s*\[([A-Za-z0-9_-]+)\](?:\[([A-Za-z]+)\])?\s+(.+)$",
            stripped,
        )
        if not match:
            continue

        package = match.group(1).strip()
        if package not in PACKAGE_ORDER:
            raise SystemExit(
                f"Unknown package '{package}' in unreleased changelog. "
                f"Use one of: {', '.join(PACKAGE_ORDER)}"
            )
        category = _normalize_category(match.group(2))
        message = match.group(3).strip()
        result[category].setdefault(package, []).append(f"- {message}")

    return result


def _package_sort_key(package: str) -> tuple[int, str]:
    if package in PACKAGE_ORDER:
        return (PACKAGE_ORDER.index(package), package)
    return (len(PACKAGE_ORDER), package)


def _build_release_body(sections: dict[str, dict[str, list[str]]]) -> str:
    """Format unreleased entries into a changelog body."""
    parts = []
    for cat in CHANGELOG_CATEGORIES:
        package_parts = []
        for package in sorted(sections[cat], key=_package_sort_key):
            entries = sections[cat][package]
            if entries:
                package_parts.append(f"#### {package}\n" + "\n".join(entries))
        if package_parts:
            parts.append(f"### {cat}\n\n" + "\n\n".join(package_parts))

    return "\n\n".join(parts).strip()


def _prepend_changelog(version_str: str, body: str):
    today = date.today().isoformat()
    new_entry = f"## [{version_str}] — {today}\n\n{body}\n"

    existing = ""
    if CHANGELOG.exists():
        raw = CHANGELOG.read_text(encoding="utf-8")
        # Strip our own header so we don't duplicate it
        if raw.startswith("# Changelog"):
            # Find the first ## entry and keep everything from there
            m = re.search(r"^## \[", raw, re.MULTILINE)
            existing = raw[m.start():] if m else ""
        else:
            existing = raw

    CHANGELOG.write_text(
        CHANGELOG_HEADER + new_entry + "\n" + existing,
        encoding="utf-8",
    )


def _reset_unreleased() -> None:
    """Reset unreleased_changelog.md to the empty template."""
    UNRELEASED.write_text(UNRELEASED_TEMPLATE, encoding="utf-8")


# ── Git helpers ───────────────────────────────────────────────────────────────

def _run(cmd: list[str]):
    result = subprocess.run(cmd, cwd=ROOT)
    if result.returncode != 0:
        raise SystemExit(f"Command failed: {' '.join(cmd)}")


def _commit_and_tag(version_str: str):
    tag = f"v{version_str}"
    _run(["git", "add",
          str(PYPROJECT), str(CHANGELOG), str(UNRELEASED)])
    _run(["git", "commit", "-m", f"chore: release {tag}"])
    _run(["git", "tag", "-f", tag])
    print(f"\nTagged {tag}. Push with:")
    print(f"  git push && git push origin {tag}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) != 2 or sys.argv[1] not in VALID_BUMPS:
        print("Usage: python scripts/release.py patch|minor|major")
        sys.exit(1)

    bump_type = sys.argv[1]
    sections = _parse_unreleased()
    body = _build_release_body(sections)
    if not body:
        print("Nothing to release in docs/unreleased_changelog.md")
        print("Add entries to unreleased_changelog.md first.")
        sys.exit(1)

    old_version = _read_version()
    new_version = _bump(old_version, bump_type)
    version_str = _write_version(new_version)

    old_str = "%d.%d.%d" % old_version
    print(f"Bumping {old_str} -> {version_str}  ({bump_type})")
    print("Release notes:")
    print("-" * 40)
    print(body)
    print("-" * 40)

    _prepend_changelog(version_str, body)
    _reset_unreleased()
    _commit_and_tag(version_str)


if __name__ == "__main__":
    main()
