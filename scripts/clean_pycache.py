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
"""Remove Python __pycache__ directories from the workspace."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def _iter_pycache_dirs(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("__pycache__") if path.is_dir())


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Remove all __pycache__ directories below a workspace root."
    )
    parser.add_argument(
        "root",
        nargs="?",
        default=Path(__file__).resolve().parents[1],
        type=Path,
        help="Workspace root to clean. Defaults to the repository root.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show which __pycache__ directories would be removed.",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    pycache_dirs = _iter_pycache_dirs(root)
    if not pycache_dirs:
        print(f"No __pycache__ directories found under {root}")
        return 0

    for path in pycache_dirs:
        print(path)
        if not args.dry_run:
            shutil.rmtree(path)

    action = "Would remove" if args.dry_run else "Removed"
    print(f"{action} {len(pycache_dirs)} __pycache__ director{'y' if len(pycache_dirs) == 1 else 'ies'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
