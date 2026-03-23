"""Release helper — bumps version, updates CHANGELOG, commits and tags.

Usage:
    python scripts/release.py patch   # 0.1.0 -> 0.1.1
    python scripts/release.py minor   # 0.1.0 -> 0.2.0
    python scripts/release.py major   # 0.1.0 -> 1.0.0

Changes are read from unreleased_changelog.md:
  - patch  : takes only ### patch entries
  - minor  : takes ### patch + ### minor entries
  - major  : takes all entries (### patch + ### minor + ### major)

Used sections are cleared from unreleased_changelog.md after release.
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

# Which sections to include per release type (cumulative)
SECTIONS = {
    "patch": ["patch"],
    "minor": ["minor", "patch"],
    "major": ["major", "minor", "patch"],
}


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

def _parse_unreleased() -> dict[str, list[str]]:
    """Parse unreleased_changelog.md into {section: [lines]}."""
    text = UNRELEASED.read_text(encoding="utf-8")
    result: dict[str, list[str]] = {"major": [], "minor": [], "patch": []}
    current = None
    for line in text.splitlines():
        m = re.match(r"^###\s+(major|minor|patch)", line)
        if m:
            current = m.group(1)
            continue
        if line.startswith("#"):
            current = None
            continue
        if current and line.strip() and not line.strip().startswith("<!--"):
            result[current].append(line.rstrip())
    return result


def _format_section(title: str, lines: list[str]) -> str:
    if not lines:
        return ""
    return f"### {title}\n" + "\n".join(lines) + "\n"


def _build_release_body(sections: dict[str, list[str]], include: list[str]) -> str:
    parts = []
    for name in ["major", "minor", "patch"]:
        if name in include:
            part = _format_section(name, sections[name])
            if part:
                parts.append(part)
    return "\n".join(parts).strip()


def _prepend_changelog(version_str: str, body: str):
    today = date.today().isoformat()
    header = f"## [{version_str}] - {today}\n\n{body}\n"
    existing = CHANGELOG.read_text(encoding="utf-8") if CHANGELOG.exists() else ""
    CHANGELOG.write_text(header + "\n" + existing, encoding="utf-8")


def _clear_unreleased_sections(include: list[str]):
    """Remove used sections from unreleased_changelog.md."""
    text = UNRELEASED.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    result = []
    skip = False
    for line in lines:
        m = re.match(r"^###\s+(major|minor|patch)", line)
        if m:
            skip = m.group(1) in include
            result.append(line)
            continue
        if line.startswith("#"):
            skip = False
        if not skip or not line.strip() or line.strip().startswith("<!--"):
            result.append(line)
        # Drop content lines in used sections
    UNRELEASED.write_text("".join(result), encoding="utf-8")


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
    _run(["git", "tag", tag])
    print(f"\nTagged {tag}. Push with:")
    print(f"  git push && git push origin {tag}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) != 2 or sys.argv[1] not in SECTIONS:
        print("Usage: python scripts/release.py patch|minor|major")
        sys.exit(1)

    bump_type = sys.argv[1]
    include   = SECTIONS[bump_type]

    # Read and validate unreleased entries
    sections = _parse_unreleased()
    body = _build_release_body(sections, include)
    if not body:
        print(f"Nothing to release in sections: {include}")
        print("Add entries to unreleased_changelog.md first.")
        sys.exit(1)

    # Bump version
    old_version = _read_version()
    new_version = _bump(old_version, bump_type)
    version_str = _write_version(new_version)

    old_str = "%d.%d.%d" % old_version
    print(f"Bumping {old_str} -> {version_str}  ({bump_type})")
    print(f"Sections included: {include}\n")
    print("Release notes:")
    print("-" * 40)
    print(body)
    print("-" * 40)

    # Update changelogs
    _prepend_changelog(version_str, body)
    _clear_unreleased_sections(include)

    # Commit and tag
    _commit_and_tag(version_str)


if __name__ == "__main__":
    main()
