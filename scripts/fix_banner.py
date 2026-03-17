#!/usr/bin/env python3
"""Fix or insert the canonical TinyUI license banner in Python files.

Usage:
    python scripts/fix_banner.py [FILES...]

If no files are given, processes all staged .py files (for pre-commit use).
Exits 1 when any file was changed so the commit is retried with the fix.
"""

import re
import subprocess
import sys
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

# Directories that contain our own source (relative to repo root)
SRC_DIRS = ("src/tinyui", "src/tinycore", "src/plugins")

# Skip auto-generated files
SKIP_MARKERS = ("# Auto-generated",)

# Regex that matches any old/current banner variant.
# Catches everything from the first "#  TinyUI" line through the
# "licensed under GPLv3." line (with optional trailing comment).
_OLD_BANNER_RE = re.compile(
    r"^(#  TinyUI[^\n]*\n"       # first line: "#  TinyUI" with optional suffix
    r"(?:#[^\n]*\n)*?"           # comment lines (copyright, license text, etc.)
    r"#  licensed under GPLv3\."  # anchor: always the last real line
    r"[^\n]*\n)"                 # rest of that line + newline
    r"\n?",                      # optional blank line after banner
    re.MULTILINE,
)


def _is_src_file(path: Path) -> bool:
    """Only touch files inside our source directories."""
    s = path.as_posix()
    return any(s.startswith(d) or ("/" + d) in s for d in SRC_DIRS)


def _should_skip(content: str) -> bool:
    """Skip auto-generated files and empty __init__.py."""
    if not content.strip():
        return True
    for marker in SKIP_MARKERS:
        if content.startswith(marker):
            return True
    return False


def fix_file(path: Path) -> bool:
    """Fix the banner in a single file. Returns True if file was changed."""
    content = path.read_text(encoding="utf-8")

    if _should_skip(content):
        return False

    # Already correct?
    if content.startswith(BANNER):
        return False

    # Has an old/wrong banner? Replace it.
    if _OLD_BANNER_RE.match(content):
        new_content = _OLD_BANNER_RE.sub(BANNER + "\n", content, count=1)
    else:
        # No banner at all — prepend it.
        # Preserve shebang if present.
        if content.startswith("#!"):
            first_nl = content.index("\n") + 1
            shebang = content[:first_nl]
            rest = content[first_nl:].lstrip("\n")
            new_content = shebang + "\n" + BANNER + "\n" + rest
        else:
            new_content = BANNER + "\n" + content

    if new_content == content:
        return False

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
        # Re-stage fixed files
        if len(sys.argv) <= 1:
            subprocess.run(["git", "add"] + [str(p) for p in changed])
        print(f"\n  {len(changed)} file(s) fixed")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
