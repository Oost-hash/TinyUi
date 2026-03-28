"""Regenerate QML type info into .qml_linter and run qmllint."""

from __future__ import annotations

import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
LINTER_ROOT = ROOT / ".qml_linter"


@dataclass(frozen=True)
class QmlModule:
    import_name: str
    package_dir: Path
    qml_dir: Path


MODULES = [
    QmlModule("TinyUI", SRC / "tinyui", SRC / "tinyui" / "qml"),
    QmlModule("TinyDevTools", SRC / "tinydevtools", SRC / "tinydevtools" / "qml"),
    QmlModule("TinyWidgets", SRC / "tinywidgets", SRC / "tinywidgets" / "qml"),
]


def find_tool(name: str, *, libexec: bool = False) -> Path:
    suffix = ".exe" if sys.platform == "win32" else ""
    base = ROOT / ".venv" / "Lib" / "site-packages" / "PySide6"
    if libexec:
        tool = base / "Qt" / "libexec" / f"{name}{suffix}"
        if tool.exists():
            return tool
    else:
        tool = base / f"{name}{suffix}"
        if tool.exists():
            return tool

    script_dir = ROOT / ".venv" / ("Scripts" if sys.platform == "win32" else "bin")
    fallback = script_dir / f"pyside6-{name}{suffix}"
    return fallback


QMLLINT = find_tool("qmllint")
METAOBJECTDUMP = find_tool("metaobjectdump")
QMLTYPEREGISTRAR = find_tool("qmltyperegistrar", libexec=True)


def run_checked(cmd: list[str | Path]) -> None:
    command = [str(part) for part in cmd]
    result = subprocess.run(command, cwd=ROOT)
    if result.returncode != 0:
        raise subprocess.CalledProcessError(result.returncode, command)


def qml_python_sources(module: QmlModule) -> list[Path]:
    sources: list[Path] = []
    for path in sorted(module.package_dir.rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        if "QML_IMPORT_NAME" in text and "@QmlElement" in text:
            sources.append(path)
    return sources


def regenerate_module(module: QmlModule) -> Path:
    output_dir = LINTER_ROOT / module.import_name
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    qmltypes_files: list[Path] = []
    for source in qml_python_sources(module):
        metatypes_json = output_dir / f"{source.stem}metatypes.json"
        qmltypes_file = output_dir / f"{source.stem}.qmltypes"
        registrar_cpp = output_dir / f"{source.stem}_qmltyperegistrations.cpp"

        run_checked([METAOBJECTDUMP, "-o", metatypes_json, source])
        run_checked(
            [
                QMLTYPEREGISTRAR,
                "--generate-qmltypes",
                qmltypes_file,
                "-o",
                registrar_cpp,
                metatypes_json,
                "--import-name",
                module.import_name,
                "--major-version",
                "1",
                "--minor-version",
                "0",
            ]
        )
        qmltypes_files.append(qmltypes_file)

    qmldir = output_dir / "qmldir"
    lines = [f"module {module.import_name}"]
    lines.extend(f"typeinfo {path.name}" for path in qmltypes_files)
    qmldir.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return qmldir


def qml_files() -> list[Path]:
    files: list[Path] = []
    for module in MODULES:
        files.extend(sorted(module.qml_dir.rglob("*.qml")))
    return files


def main() -> int:
    missing = [tool for tool in (QMLLINT, METAOBJECTDUMP, QMLTYPEREGISTRAR) if not tool.exists()]
    if missing:
        for tool in missing:
            print(f"error: required tool not found at {tool}")
        print("Make sure the venv is set up: python -m pip install pyside6")
        return 1

    files = qml_files()
    if not files:
        print("No QML files found.")
        return 0

    qmldirs = [regenerate_module(module) for module in MODULES]

    cmd = [str(QMLLINT)]
    for qmldir in qmldirs:
        cmd.extend(["-i", str(qmldir)])
    cmd.extend(str(path) for path in files)

    result = subprocess.run(cmd, cwd=ROOT)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
