# -*- mode: python ; coding: utf-8 -*-

from __future__ import annotations

from pathlib import Path

from PyInstaller.building.build_main import Analysis, COLLECT, EXE, PYZ
from PyInstaller.utils.hooks import collect_submodules

ROOT = Path(SPECPATH)
SRC = ROOT / "src"


def collect_non_python_files(source: Path, target_prefix: str) -> list[tuple[str, str]]:
    datas: list[tuple[str, str]] = []
    for path in sorted(source.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(source)
        if "__pycache__" in rel.parts:
            continue
        if path.suffix in {".py", ".pyc", ".pyo"}:
            continue
        datas.append((str(path), str(Path(target_prefix) / rel.parent)))
    return datas


datas = [
    *collect_non_python_files(SRC / "ui_api" / "qml", "ui_api/qml"),
    *collect_non_python_files(SRC / "plugins" / "tinyui", "plugins/tinyui"),
]

hiddenimports = [
    "plugins.tinyui.plugin",
]

a = Analysis(
    [str(SRC / "boot.py")],
    pathex=[str(SRC)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="TinyUi",
    icon=str(ROOT / "assets" / "images" / "logo" / "logo.ico"),
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    contents_directory="tinyui",
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="TinyUi",
)
