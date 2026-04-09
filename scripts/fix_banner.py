#!/usr/bin/env python3
"""Fix or insert the canonical TinyUI license banner in Python and QML files.

Usage:
    python scripts/fix_banner.py [FILES...]
    python scripts/fix_banner.py --all

If no files are given, processes all staged .py and .qml files (for pre-commit use).
Use --all to process all source files regardless of git status.
Exits 1 when any file was changed so the commit is retried with the fix.
Backups are saved to .banner_backups/ before any changes.
"""

import argparse
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Banner body — comment prefix is added per file type
_BANNER_BODY = [
    "TinyUI",
    "Copyright (C) 2026 Oost-hash",
    "",
    "This file is part of TinyUI.",
    "",
    "TinyUI is free software: you can redistribute it and/or modify",
    "it under the terms of the GNU General Public License as published by",
    "the Free Software Foundation, either version 3 of the License, or",
    "(at your option) any later version.",
    "",
    "TinyUI is distributed in the hope that it will be useful,",
    "but WITHOUT ANY WARRANTY; without even the implied warranty of",
    "MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the",
    "GNU General Public License for more details.",
    "",
    "You should have received a copy of the GNU General Public License",
    "along with this program.  If not, see <https://www.gnu.org/licenses/>.",
    "",
    "TinyUI builds on TinyPedal by s-victor (https://github.com/s-victor/TinyPedal),",
    "licensed under GPLv3.",
]


def _make_banner(prefix: str) -> str:
    return (
        "\n".join(
            f"{prefix}  {line}".rstrip() if line else prefix for line in _BANNER_BODY
        )
        + "\n"
    )


# Per-extension config: (banner, comment_char)
_EXT_CONFIG: dict[str, tuple[str, str]] = {
    ".py": (_make_banner("#"), "#"),
    ".qml": (_make_banner("//"), "//"),
}

# Directories that contain our own source (relative to repo root)
SRC_DIRS = (
    "src/runtime",
    "src/runtimeV2",
    "src/runtime_schema",
    "src/app_schema",
    "src/ui_api",
    "src/widget_api",
    "src/shared_runtime_host",
    "src/pkg_runtime_host",
    "src/capabilities",
    "src/plugins",
)

# Fingerprints: if any of these appear in the first 30 lines, it's a banner.
_FINGERPRINTS = [
    "This file is part of TinyUI",
    "TinyUI is free software",
    "GNU General Public License",
    "licensed under GPLv3",
]

# Backup directory
BACKUP_DIR = Path(".banner_backups")


def _is_src_file(path: Path) -> bool:
    """Only touch files inside our source directories."""
    s = path.as_posix()
    return any(s.startswith(d) or ("/" + d) in s for d in SRC_DIRS)


def _should_skip(content: str) -> bool:
    """Skip auto-generated and empty files."""
    if not content.strip():
        return True
    return content.startswith("# Auto-generated") or content.startswith(
        "// Auto-generated"
    )


def _find_banner_end(lines: list[str], comment_char: str) -> int:
    """Return the index of the first non-banner line.

    Scans from the top through the leading comment block. If the block
    contains enough license fingerprints, the whole block is considered
    a banner and its end index is returned. Returns 0 if no banner found.
    """
    head = "\n".join(lines[:30])
    if sum(1 for fp in _FINGERPRINTS if fp in head) < 2:
        return 0

    end = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(comment_char) or stripped == "":
            end = i + 1
        else:
            break
    return end


def _backup(path: Path) -> None:
    """Create a timestamped backup of the file."""
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / stamp / path
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        shutil.copy2(path, backup_path)
    except (PermissionError, OSError) as e:
        print(f"  warning: could not backup {path}: {e}")


def fix_file(path: Path) -> bool:
    """Fix the banner in a single file. Returns True if file was changed."""
    config = _EXT_CONFIG.get(path.suffix)
    if config is None:
        return False

    banner, comment_char = config
    content = path.read_text(encoding="utf-8")

    if _should_skip(content) or content.startswith(banner):
        return False

    lines = content.splitlines(keepends=True)

    # Preserve shebang (Python only)
    shebang = ""
    if path.suffix == ".py" and lines and lines[0].startswith("#!"):
        shebang = lines[0]
        lines = lines[1:]
        while lines and lines[0].strip() == "":
            lines = lines[1:]

    rest = lines[_find_banner_end(lines, comment_char) :]
    while rest and rest[0].strip() == "":
        rest = rest[1:]

    new_content = (shebang + "\n" if shebang else "") + banner + "\n" + "".join(rest)

    if new_content == content:
        return False

    _backup(path)
    path.write_text(new_content, encoding="utf-8")
    return True


def get_staged_files() -> list[Path]:
    """Get .py and .qml files staged for commit."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        capture_output=True,
        text=True,
    )
    return [
        Path(f)
        for f in result.stdout.strip().splitlines()
        if Path(f).suffix in _EXT_CONFIG and _is_src_file(Path(f))
    ]


def get_all_src_files(repo_root: Path) -> list[Path]:
    """Get all .py and .qml files in source directories."""
    files = []
    for src_dir in SRC_DIRS:
        dir_path = repo_root / src_dir
        if dir_path.exists():
            for ext in _EXT_CONFIG:
                files.extend(dir_path.rglob(f"*{ext}"))
    return [f for f in files if _is_src_file(f)]


def main() -> int:
    parser = argparse.ArgumentParser(description="Fix or insert the canonical TinyUI license banner.")
    parser.add_argument("files", nargs="*", help="Specific files to process")
    parser.add_argument("--all", action="store_true", help="Process all source files (not just staged)")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]

    if args.files:
        files = [Path(f) for f in args.files if Path(f).suffix in _EXT_CONFIG]
    elif args.all:
        files = get_all_src_files(repo_root)
    else:
        files = get_staged_files()

    changed = []
    for path in files:
        if path.exists() and fix_file(path):
            changed.append(path)
            print(f"  fixed: {path}")

    if changed:
        print(f"  backups in: {BACKUP_DIR.resolve()}")
        if not args.files:  # Only auto-add if not given explicit files
            subprocess.run(["git", "add"] + [str(p) for p in changed])
        print(f"  {len(changed)} file(s) fixed")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
