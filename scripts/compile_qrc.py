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

This script collects app-owned and plugin-owned QRC declarations into one
generated build QRC, then compiles it into pkg_runtime_host.resources_rc.

Usage:
    python scripts/compile_qrc.py
    python scripts/compile_qrc.py --watch  # Auto-recompile on changes
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP_QRC_FILE = ROOT / "resources.qrc"
GENERATED_QRC_FILE = ROOT / "build" / "qrc" / "resources.qrc"
OUTPUT_FILE = ROOT / "src" / "pkg_runtime_host" / "resources_rc.py"


def _qrc_inputs() -> list[Path]:
    """Return app and plugin QRC declarations in stable order."""

    plugin_qrc_files = sorted((ROOT / "src" / "plugins").glob("*/resources.qrc"))
    return [APP_QRC_FILE, *plugin_qrc_files]


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


def _resource_file_path(qrc_file: Path, element: ET.Element) -> str:
    """Return an absolute resource path for a generated aggregate QRC entry."""

    text = (element.text or "").strip()
    if not text:
        raise ValueError(f"Empty resource file entry in {qrc_file}")
    source_path = Path(text)
    if not source_path.is_absolute():
        source_path = qrc_file.parent / source_path
    return source_path.resolve().as_posix()


def _write_aggregate_qrc(qrc_files: list[Path]) -> Path:
    """Write one generated QRC from app and plugin declarations."""

    missing = [qrc_file for qrc_file in qrc_files if not qrc_file.exists()]
    if missing:
        missing_text = ", ".join(str(path) for path in missing)
        raise FileNotFoundError(f"QRC declaration not found: {missing_text}")

    root = ET.Element("RCC")
    resources_by_prefix: dict[str, ET.Element] = {}
    for qrc_file in qrc_files:
        qrc_tree = ET.parse(qrc_file)
        qrc_root = qrc_tree.getroot()
        for qresource in qrc_root.findall("qresource"):
            prefix = qresource.attrib.get("prefix", "/")
            aggregate_resource = resources_by_prefix.get(prefix)
            if aggregate_resource is None:
                aggregate_resource = ET.SubElement(root, "qresource", {"prefix": prefix})
                resources_by_prefix[prefix] = aggregate_resource
            for file_element in qresource.findall("file"):
                aggregate_file = ET.SubElement(aggregate_resource, "file")
                alias = file_element.attrib.get("alias")
                if alias:
                    aggregate_file.set("alias", alias)
                aggregate_file.text = _resource_file_path(qrc_file, file_element)

    GENERATED_QRC_FILE.parent.mkdir(parents=True, exist_ok=True)
    ET.indent(root, space="    ")
    ET.ElementTree(root).write(GENERATED_QRC_FILE, encoding="utf-8", xml_declaration=False)
    return GENERATED_QRC_FILE


def compile_qrc() -> int:
    """Compile QRC declarations to pkg_runtime_host.resources_rc."""
    rcc = _find_rcc()
    if rcc is None:
        print("Error: pyside6-rcc not found. Is PySide6 installed?")
        return 1

    try:
        qrc_file = _write_aggregate_qrc(_qrc_inputs())
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}")
        return 1

    print(f"Compiling {qrc_file}...")
    cmd = [rcc, "-o", str(OUTPUT_FILE), str(qrc_file)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return result.returncode
    
    size = OUTPUT_FILE.stat().st_size
    print(f"[OK] Compiled to {OUTPUT_FILE} ({size:,} bytes)")
    return 0


def watch_qrc() -> int:
    """Watch for changes and auto-recompile."""

    def watched_files() -> dict[Path, float]:
        files: dict[Path, float] = {}
        patterns = [
            ROOT / "resources.qrc",
            *ROOT.glob("src/plugins/*/resources.qrc"),
            *ROOT.glob("src/**/*.qml"),
            *ROOT.glob("assets/**/*"),
        ]
        for path in patterns:
            if path.is_file():
                files[path] = path.stat().st_mtime
        return files

    print(f"Watching QRC declarations and resources...")
    print("Press Ctrl+C to stop\n")

    compile_qrc()
    previous = watched_files()

    try:
        while True:
            time.sleep(1)
            current = watched_files()
            if current != previous:
                print("\nDetected QRC/resource change")
                compile_qrc()
                previous = current
    except KeyboardInterrupt:
        print("\nStopped watching.")
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
