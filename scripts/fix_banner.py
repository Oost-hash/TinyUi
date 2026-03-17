#!/usr/bin/env python3
"""Fix or insert the canonical TinyUI license banner in Python files.

Usage:
    python scripts/fix_banner.py [FILES...]

If no files are given, processes all staged .py files (for pre-commit use).
Exits 1 when any file was changed so the commit is retried with the fix.
Backups are saved to .banner_backups/ before any changes.
"""

import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

BANNER = """\
#  TinyUI
#  Copyright (C) 2026 Oost-hash
#
#  This file is part of TinyUI.
#
#  TinyUI is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  TinyUI is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#  TinyUI builds on TinyPedal by s-victor (https://github.com/s-victor/TinyPedal),
#  licensed under GPLv3.
"""

BANNER_LINES = BANNER.strip().splitlines()

# Directories that contain our own source (relative to repo root)
SRC_DIRS = ("src/tinyui", "src/tinycore", "src/plugins")

# Skip auto-generated files
SKIP_MARKERS = ("# Auto-generated",)

# Fingerprints: if any of these appear in the first 25 lines, it's a banner.
# This is much more robust than a single regex — catches any variant.
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
    """Skip auto-generated files and empty files."""
    if not content.strip():
        return True
    for marker in SKIP_MARKERS:
        if content.startswith(marker):
            return True
    return False


def _find_banner_end(lines: list[str]) -> int:
    """Find where the existing banner ends.

    Scans from the top through the leading comment block. If the block
    contains enough license fingerprints, the whole block is considered
    a banner. Returns the index of the first non-banner line.
    """
    # First check: does this file even have a banner?
    head = "\n".join(lines[:30])
    matches = sum(1 for fp in _FINGERPRINTS if fp in head)
    if matches < 2:
        return 0  # Not a banner

    # Find the end of the leading comment block (comments + blank lines)
    end = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("#") or stripped == "":
            end = i + 1
        else:
            break

    return end


def _backup(path: Path) -> Path:
    """Create a timestamped backup of the file."""
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / stamp / path
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, backup_path)
    return backup_path


def fix_file(path: Path) -> bool:
    """Fix the banner in a single file. Returns True if file was changed."""
    content = path.read_text(encoding="utf-8")

    if _should_skip(content):
        return False

    # Already correct?
    if content.startswith(BANNER):
        return False

    lines = content.splitlines(keepends=True)

    # Preserve shebang
    shebang = ""
    if lines and lines[0].startswith("#!"):
        shebang = lines[0]
        lines = lines[1:]
        # Skip blank lines after shebang
        while lines and lines[0].strip() == "":
            lines = lines[1:]

    banner_end = _find_banner_end(lines)
    rest = lines[banner_end:]

    # Strip leading blank lines from rest
    while rest and rest[0].strip() == "":
        rest = rest[1:]

    new_content = shebang
    if shebang:
        new_content += "\n"
    new_content += BANNER + "\n" + "".join(rest)

    if new_content == content:
        return False

    _backup(path)
    path.write_text(new_content, encoding="utf-8")
    return True


def get_staged_py_files() -> list[Path]:
    """Get .py files staged for commit."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        capture_output=True,
        text=True,
    )
    return [
        Path(f)
        for f in result.stdout.strip().splitlines()
        if f.endswith(".py") and _is_src_file(Path(f))
    ]


def main():
    if len(sys.argv) > 1:
        files = [Path(f) for f in sys.argv[1:] if f.endswith(".py")]
    else:
        files = get_staged_py_files()

    changed = []
    for path in files:
        if not path.exists():
            continue
        if fix_file(path):
            changed.append(path)
            print(f"  fixed: {path}")

    if changed:
        print(f"  backups in: {BACKUP_DIR.resolve()}")
        # Re-stage fixed files
        if len(sys.argv) <= 1:
            subprocess.run(["git", "add"] + [str(p) for p in changed])
        print(f"  {len(changed)} file(s) fixed")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
