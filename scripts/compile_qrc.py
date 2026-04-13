#!/usr/bin/env python3
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

"""Compile QRC resources for the TinyUI build.

This script compiles the resources.qrc file into src/resources_rc.py
which is then included in the PyInstaller build.

Usage:
    python scripts/compile_qrc.py
    python scripts/compile_qrc.py --watch  # Auto-recompile on changes
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QRC_FILE = ROOT / "resources.qrc"
OUTPUT_FILE = ROOT / "src" / "resources_rc.py"


def _find_rcc() -> str | None:
    """Find the pyside6-rcc executable."""
    # Try venv first
    if sys.platform == "win32":
        venv_rcc = ROOT / ".venv" / "Scripts" / "pyside6-rcc.exe"
    else:
        venv_rcc = ROOT / ".venv" / "bin" / "pyside6-rcc"
    
    if venv_rcc.exists():
        return str(venv_rcc)
    
    # Try PATH
    rcc = shutil.which("pyside6-rcc")
    return rcc


def compile_qrc() -> int:
    """Compile resources.qrc to src/resources_rc.py."""
    rcc = _find_rcc()
    if rcc is None:
        print("Error: pyside6-rcc not found. Is PySide6 installed?")
        return 1
    
    if not QRC_FILE.exists():
        print(f"Error: {QRC_FILE} not found.")
        return 1
    
    print(f"Compiling {QRC_FILE}...")
    cmd = [rcc, "-o", str(OUTPUT_FILE), str(QRC_FILE)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return result.returncode
    
    size = OUTPUT_FILE.stat().st_size
    print(f"[OK] Compiled to {OUTPUT_FILE} ({size:,} bytes)")
    return 0


def watch_qrc() -> int:
    """Watch for changes and auto-recompile."""
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
    except ImportError:
        print("Error: watchdog not installed. Run: pip install watchdog")
        return 1
    
    class QrcHandler(FileSystemEventHandler):
        def on_modified(self, event):
            if event.src_path.endswith((".qrc", ".qml")):
                print(f"\nDetected change in {event.src_path}")
                compile_qrc()
    
    print(f"Watching {QRC_FILE.parent} for changes...")
    print("Press Ctrl+C to stop\n")
    
    # Initial compile
    compile_qrc()
    
    observer = Observer()
    handler = QrcHandler()
    
    # Watch root for qrc changes
    observer.schedule(handler, str(ROOT), recursive=False)
    # Watch src for qml changes
    observer.schedule(handler, str(ROOT / "src"), recursive=True)
    # Watch assets
    observer.schedule(handler, str(ROOT / "assets"), recursive=True)
    
    observer.start()
    try:
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\nStopped watching.")
    observer.join()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Compile QRC resources for TinyUI")
    parser.add_argument("--watch", "-w", action="store_true", help="Watch for changes and auto-recompile")
    args = parser.parse_args()
    
    if args.watch:
        return watch_qrc()
    return compile_qrc()


if __name__ == "__main__":
    sys.exit(main())
