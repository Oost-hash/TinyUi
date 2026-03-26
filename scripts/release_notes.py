"""Shared helpers for version-tagged unreleased release notes."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

CHANGELOG_CATEGORIES = ("Added", "Changed", "Fixed", "Removed")
PACKAGE_ORDER = ("app", "plugins", "tinycore", "tinyui", "tinywidgets", "other")


@dataclass(frozen=True)
class UnreleasedEntry:
    version: str
    package: str
    category: str
    message: str


def normalize_category(raw: str | None) -> str:
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


def parse_unreleased(path: Path) -> tuple[str, list[UnreleasedEntry]]:
    """Parse unreleased_changelog.md into a preserved header and typed entries."""
    text = path.read_text(encoding="utf-8")
    header_lines: list[str] = []
    entries: list[UnreleasedEntry] = []
    in_entries = False

    for line in text.splitlines():
        stripped = line.strip()
        if stripped == "## Entries":
            in_entries = True
            header_lines.append(line)
            continue
        if not in_entries:
            header_lines.append(line)
            continue
        if not stripped or stripped.startswith("#"):
            continue
        match = re.match(
            r"^-\s*\[(\d+\.\d+\.\d+)\]\[([A-Za-z0-9_-]+)\](?:\[([A-Za-z]+)\])?\s+(.+)$",
            stripped,
        )
        if not match:
            continue

        version = match.group(1).strip()
        package = match.group(2).strip()
        if package not in PACKAGE_ORDER:
            raise SystemExit(
                f"Unknown package '{package}' in unreleased changelog. "
                f"Use one of: {', '.join(PACKAGE_ORDER)}"
            )
        category = normalize_category(match.group(3))
        message = match.group(4).strip()
        entries.append(
            UnreleasedEntry(
                version=version,
                package=package,
                category=category,
                message=message,
            )
        )

    return "\n".join(header_lines).rstrip() + "\n", entries


def sections_for_version(
    entries: list[UnreleasedEntry],
    version: str,
) -> dict[str, dict[str, list[str]]]:
    """Group unreleased entries for one version by category and package."""
    result: dict[str, dict[str, list[str]]] = {
        category: {} for category in CHANGELOG_CATEGORIES
    }
    for entry in entries:
        if entry.version != version:
            continue
        result[entry.category].setdefault(entry.package, []).append(f"- {entry.message}")
    return result


def package_sort_key(package: str) -> tuple[int, str]:
    if package in PACKAGE_ORDER:
        return (PACKAGE_ORDER.index(package), package)
    return (len(PACKAGE_ORDER), package)


def build_release_body(sections: dict[str, dict[str, list[str]]]) -> str:
    """Format unreleased entries into a changelog body."""
    parts = []
    for category in CHANGELOG_CATEGORIES:
        package_parts = []
        for package in sorted(sections[category], key=package_sort_key):
            grouped_entries = sections[category][package]
            if grouped_entries:
                package_parts.append(f"#### {package}\n" + "\n".join(grouped_entries))
        if package_parts:
            parts.append(f"### {category}\n\n" + "\n\n".join(package_parts))

    return "\n\n".join(parts).strip()


def write_unreleased(path: Path, header: str, entries: list[UnreleasedEntry]) -> None:
    """Rewrite unreleased_changelog.md with remaining version-tagged entries."""
    lines = [header.rstrip(), ""]
    for entry in entries:
        category = entry.category.lower()
        if category == "added":
            lines.append(f"- [{entry.version}][{entry.package}] {entry.message}")
        else:
            lines.append(f"- [{entry.version}][{entry.package}][{category}] {entry.message}")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
