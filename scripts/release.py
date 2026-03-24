"""Release helper — bumps version, updates CHANGELOG, commits and tags.

Usage:
    python scripts/release.py patch   # 0.1.0 -> 0.1.1
    python scripts/release.py minor   # 0.1.0 -> 0.2.0
    python scripts/release.py major   # 0.1.0 -> 1.0.0

Changes are read from unreleased_changelog.md:
  - patch  : takes only ### patch entries
  - minor  : takes ### patch + ### minor entries
  - major  : takes all entries (### patch + ### minor + ### major)

Entries are automatically sorted into ### Added / ### Changed / ### Fixed /
### Removed based on keywords in the entry text:
  - Removed  : starts with "Removed" or contains "removed from"
  - Fixed    : contains " now " (was broken, now works) or starts with "Fixed"
  - Added    : minor/major entry that is not Removed or Changed
  - Changed  : everything else

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

CHANGELOG_HEADER = """\
# Changelog

All notable changes to TinyUI are documented here.
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

"""

# Which unreleased sections to include per release type (cumulative)
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


def _categorize(line: str, source_section: str) -> str:
    """Return 'Added', 'Changed', 'Fixed', or 'Removed' based on keywords."""
    text = line.lstrip("- ").strip()

    # Removed — explicit keyword
    if re.match(r"Removed\b", text) or "removed from" in text.lower():
        return "Removed"

    # Fixed — "now" indicates something that was previously broken
    if re.search(r"\bnow\b", text) or re.match(r"Fixed\b", text, re.IGNORECASE):
        return "Fixed"

    # Changed — refactoring / moves / structural work
    changed_words = ("moved", "refactored", "extracted", "aligned",
                     "changed from", "bumped", "replaced", "renamed", "updated")
    if any(w in text.lower() for w in changed_words):
        return "Changed"

    # minor / major entries that aren't Removed/Fixed/Changed → Added
    if source_section in ("minor", "major"):
        return "Added"

    # Remaining patch entries → Changed
    return "Changed"


def _build_release_body(sections: dict[str, list[str]], include: list[str]) -> str:
    """Categorize all included entries and format into Added/Changed/Fixed/Removed."""
    buckets: dict[str, list[str]] = {
        "Added": [], "Changed": [], "Fixed": [], "Removed": [],
    }

    for section_name in ["major", "minor", "patch"]:
        if section_name not in include:
            continue
        for line in sections[section_name]:
            cat = _categorize(line, section_name)
            buckets[cat].append(line)

    parts = []
    for cat in ("Added", "Changed", "Fixed", "Removed"):
        if buckets[cat]:
            parts.append(f"### {cat}\n" + "\n".join(buckets[cat]))

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


def _clear_unreleased_sections(include: list[str]):
    """Remove used content lines from unreleased_changelog.md."""
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
    _run(["git", "tag", "-f", tag])
    print(f"\nTagged {tag}. Push with:")
    print(f"  git push && git push origin {tag}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) != 2 or sys.argv[1] not in SECTIONS:
        print("Usage: python scripts/release.py patch|minor|major")
        sys.exit(1)

    bump_type = sys.argv[1]
    include   = SECTIONS[bump_type]

    sections = _parse_unreleased()
    body = _build_release_body(sections, include)
    if not body:
        print(f"Nothing to release in sections: {include}")
        print("Add entries to unreleased_changelog.md first.")
        sys.exit(1)

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

    _prepend_changelog(version_str, body)
    _clear_unreleased_sections(include)
    _commit_and_tag(version_str)


if __name__ == "__main__":
    main()
