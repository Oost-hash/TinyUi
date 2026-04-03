"""Release helper — releases a tagged unreleased version, updates CHANGELOG, commits and tags."""

from __future__ import annotations

import re
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT         = Path(__file__).parent.parent
PYPROJECT    = ROOT / "pyproject.toml"
CHANGELOG    = ROOT / "docs" / "CHANGELOG.md"
UNRELEASED   = ROOT / "docs" / "unreleased_changelog.md"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.release_notes import (  # noqa: E402
    build_release_body,
    parse_unreleased,
    sections_for_version,
    write_unreleased,
)

CHANGELOG_HEADER = """\
# Changelog

All notable changes to TinyUI are documented here.
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

"""

VALID_BUMPS = {"patch", "minor", "major"}
SPECIAL_VERSION_MODES = {"auto-minor"}
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")


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


def _latest_semver_tag() -> tuple[int, int, int] | None:
    result = subprocess.run(
        ["git", "tag", "--list", "v*", "--sort=-version:refname"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        return None
    for raw_line in result.stdout.splitlines():
        tag = raw_line.strip()
        if not tag:
            continue
        match = re.fullmatch(r"v(\d+)\.(\d+)\.(\d+)", tag)
        if match is None:
            continue
        return int(match.group(1)), int(match.group(2)), int(match.group(3))
    return None


def _auto_minor_from_latest_tag() -> str:
    latest = _latest_semver_tag()
    if latest is None:
        return "0.1.0"
    major, minor, _patch = latest
    return f"{major}.{minor + 1}.0"


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


def _prepend_changelog(version_str: str, body: str):
    today = date.today().isoformat()
    new_entry = f"## [{version_str}] — {today}\n\n{body}\n"

    existing = ""
    if CHANGELOG.exists():
        raw = CHANGELOG.read_text(encoding="utf-8")
        if raw.startswith("# Changelog"):
            m = re.search(r"^## \[", raw, re.MULTILINE)
            existing = raw[m.start():] if m else ""
        else:
            existing = raw

    CHANGELOG.write_text(
        CHANGELOG_HEADER + new_entry + "\n" + existing,
        encoding="utf-8",
    )


def _run(cmd: list[str]):
    result = subprocess.run(cmd, cwd=ROOT)
    if result.returncode != 0:
        raise SystemExit(f"Command failed: {' '.join(cmd)}")


def _commit_and_tag(version_str: str):
    tag = f"v{version_str}"
    _run(["git", "add", str(PYPROJECT), str(CHANGELOG), str(UNRELEASED)])
    _run(["git", "commit", "-m", f"chore: release {tag}"])
    _run(["git", "tag", "-f", tag])
    print(f"\nTagged {tag}. Push with:")
    print(f"  git push && git push origin {tag}")


def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/prepare_release.py patch|minor|major|auto-minor|<version>")
        sys.exit(1)

    arg = sys.argv[1]
    if arg in VALID_BUMPS:
        old_version = _read_version()
        target_version = "%d.%d.%d" % _bump(old_version, arg)
    elif arg in SPECIAL_VERSION_MODES:
        old_version = _read_version()
        target_version = _auto_minor_from_latest_tag()
    elif SEMVER_RE.match(arg):
        old_version = _read_version()
        target_version = arg
    else:
        print("Usage: python scripts/prepare_release.py patch|minor|major|auto-minor|<version>")
        sys.exit(1)

    header, entries = parse_unreleased(UNRELEASED)
    sections = sections_for_version(entries, target_version)
    body = build_release_body(sections)
    if not body:
        print(f"Nothing to release for version {target_version} in docs/unreleased_changelog.md")
        print("Add version-tagged entries first.")
        sys.exit(1)

    current_version = "%d.%d.%d" % old_version
    if current_version != target_version:
        version_parts = tuple(int(part) for part in target_version.split("."))
        if len(version_parts) != 3:
            raise SystemExit(f"ERROR: invalid semantic version '{target_version}'")
        version_str = _write_version(
            (version_parts[0], version_parts[1], version_parts[2])
        )
    else:
        version_str = target_version

    print(f"Preparing release {version_str}")
    print("Release notes:")
    print("-" * 40)
    print(body)
    print("-" * 40)

    _prepend_changelog(version_str, body)
    remaining_entries = [entry for entry in entries if entry.version != version_str]
    write_unreleased(UNRELEASED, header, remaining_entries)
    _commit_and_tag(version_str)


if __name__ == "__main__":
    main()
