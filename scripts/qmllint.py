"""Run qmllint against TinyUI QML files."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path
import site
import re


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"


def find_tool(name: str) -> Path:
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
QML_DIAGNOSTIC_PATTERN = re.compile(r"^(Warning|Info|Error): .*?:\d+:\d+: ", re.MULTILINE)


def resolve_input_path(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def qml_files(paths: list[Path]) -> list[Path]:
    roots = paths or [SRC]
    files: list[Path] = []
    for raw_path in roots:
        path = resolve_input_path(raw_path)
        if path.is_file():
            if path.suffix == ".qml":
                files.append(path)
            continue
        if path.is_dir():
            files.extend(sorted(path.rglob("*.qml")))
            continue
        print(f"warning: QML path does not exist: {raw_path}")
    return sorted(set(files))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        help="Write raw qmllint output to a text file.",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="Optional QML files or directories to lint. Defaults to src/.",
    )
    args = parser.parse_args()

    if not QMLLINT.exists():
        print(f"error: required tool not found at {QMLLINT}")
        print("Make sure the venv is set up: python -m pip install pyside6")
        return 1

    files = qml_files(args.paths)
    if not files:
        print("error: no QML files found.")
        return 1
    print(f"Linting {len(files)} QML files.")

    cmd = [str(QMLLINT)]
    cmd.extend(str(path) for path in files)

    result = subprocess.run(
        cmd,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    output = result.stdout or ""

    if args.output is not None:
        output_path = resolve_input_path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output, encoding="utf-8")
        print(f"Raw qmllint output written to {output_path}")
    elif output:
        print(output, end="")

    if QML_DIAGNOSTIC_PATTERN.search(output):
        return 1
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
