"""Regenerate QML type info into .qml_linter and run qmllint."""

from __future__ import annotations

import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
import site


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
LINTER_ROOT = ROOT / ".qml_linter"


@dataclass(frozen=True)
class QmlModule:
    import_name: str
    package_dir: Path
    qml_dir: Path


MODULES = [
    QmlModule("TinyQt", SRC / "tinyqt", SRC / "TinyQt"),
    QmlModule("TinyUI", SRC / "tinyqt_main", SRC / "tinyqt_main" / "qml"),
    QmlModule("TinyDevTools", SRC / "tinyqt_devtools", SRC / "tinyqt_devtools" / "qml"),
    QmlModule("TinyWidgets", SRC / "tinywidgets", SRC / "tinywidgets" / "qml"),
]


def find_tool(name: str, *, libexec: bool = False) -> Path:
    suffix = ".exe" if sys.platform == "win32" else ""
    candidate_roots: list[Path] = []

    local_site = ROOT / ".venv" / "Lib" / "site-packages"
    if local_site.exists():
        candidate_roots.append(local_site)

    for site_dir in site.getsitepackages():
        path = Path(site_dir)
        if path.exists():
            candidate_roots.append(path)

    user_site = Path(site.getusersitepackages())
    if user_site.exists():
        candidate_roots.append(user_site)

    for site_root in candidate_roots:
        base = site_root / "PySide6"
        if libexec:
            tool = base / "Qt" / "libexec" / f"{name}{suffix}"
        else:
            tool = base / f"{name}{suffix}"
        if tool.exists():
            return tool

    script_dirs = [
        ROOT / ".venv" / ("Scripts" if sys.platform == "win32" else "bin"),
        Path(sys.executable).resolve().parent,
    ]

    for script_dir in script_dirs:
        fallback = script_dir / f"pyside6-{name}{suffix}"
        if fallback.exists():
            return fallback

    resolved = shutil.which(f"pyside6-{name}")
    if resolved is not None:
        return Path(resolved)

    resolved = shutil.which(name)
    if resolved is not None:
        return Path(resolved)

    return script_dirs[-1] / f"pyside6-{name}{suffix}"


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

    qml_component_files: list[Path] = []
    for source_qml in sorted(module.qml_dir.rglob("*.qml")):
        copied_qml = output_dir / source_qml.name
        shutil.copy2(source_qml, copied_qml)
        qml_component_files.append(copied_qml)

    qmldir = output_dir / "qmldir"
    lines = [f"module {module.import_name}"]
    lines.extend(f"typeinfo {path.name}" for path in qmltypes_files)
    lines.extend(f"{path.stem} 1.0 {path.name}" for path in qml_component_files)
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

    [regenerate_module(module) for module in MODULES]

    cmd = [str(QMLLINT)]
    cmd.extend(["-I", str(LINTER_ROOT)])
    cmd.extend(["--unqualified", "disable"])
    cmd.extend(["--unused-imports", "disable"])
    cmd.extend(["--missing-property", "disable"])
    cmd.extend(["--unresolved-type", "disable"])
    cmd.extend(["--stale-property-read", "disable"])
    cmd.extend(str(path) for path in files)

    result = subprocess.run(cmd, cwd=ROOT)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
