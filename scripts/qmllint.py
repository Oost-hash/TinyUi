"""Run pyside6-qmllint on all project QML files."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Venv-local qmllint executable
if sys.platform == "win32":
    QMLLINT = ROOT / ".venv" / "Scripts" / "pyside6-qmllint.exe"
else:
    QMLLINT = ROOT / ".venv" / "bin" / "pyside6-qmllint"

# QML module descriptors for type resolution
QMLDIRS = [
    ROOT / "qml" / "TinyUI"      / "qmldir",
    ROOT / "qml" / "TinyDevTools" / "qmldir",
    ROOT / "qml" / "TinyWidgets"  / "qmldir",
]

# All QML source directories
QML_DIRS = [
    ROOT / "src" / "tinyui"      / "qml",
    ROOT / "src" / "tinydevtools" / "qml",
    ROOT / "src" / "tinywidgets"  / "qml",
]


def main() -> int:
    if not QMLLINT.exists():
        print(f"error: qmllint not found at {QMLLINT}")
        print("Make sure the venv is set up: python -m pip install pyside6")
        return 1

    qml_files = []
    for d in QML_DIRS:
        qml_files.extend(sorted(d.rglob("*.qml")))

    if not qml_files:
        print("No QML files found.")
        return 0

    cmd = [str(QMLLINT)]
    for qmldir in QMLDIRS:
        cmd += ["-i", str(qmldir)]
    cmd += [str(f) for f in qml_files]

    result = subprocess.run(cmd, cwd=ROOT)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
