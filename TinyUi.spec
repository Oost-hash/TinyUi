# -*- mode: python ; coding: utf-8 -*-

from __future__ import annotations

import shutil
import sys
from pathlib import Path

from PyInstaller.building.build_main import Analysis, COLLECT, EXE, PYZ
from PyInstaller.utils.hooks import collect_submodules

ROOT = Path(SPECPATH)
SRC = ROOT / "src"
HOST_PLUGIN_DIR = SRC / "plugins" / "tinyui"

# Ensure compiled QRC resources exist
RESOURCES_RC = SRC / "pkg_runtime_host" / "resources_rc.py"
if not RESOURCES_RC.exists():
    print("ERROR: pkg_runtime_host/resources_rc.py not found!")
    print("Please run: python scripts/compile_qrc.py")
    sys.exit(1)

# Copy LICENSE to LICENSE.txt for distribution (user-facing)
LICENSE_TXT = ROOT / "LICENSE.txt"
shutil.copy2(ROOT / "LICENSE", LICENSE_TXT)


def collect_tree(src: Path, dst: str) -> list[tuple[str, str]]:
    items = []
    for path in sorted(src.rglob("*")):
        if not path.is_file():
            continue
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        rel_parent = path.relative_to(src).parent
        target = Path(dst) / rel_parent
        items.append((str(path), str(target)))
    return items

# QML and assets are embedded through pkg_runtime_host.resources_rc.
# LICENSE.txt is kept as a standalone file for users to read
datas = [
    (str(LICENSE_TXT), "."),
]
datas += collect_tree(HOST_PLUGIN_DIR, "plugins/tinyui")

hiddenimports = [
    "mmap",
    "plugins.tinyui.plugin",
    "pkg_runtime_host.resources_rc",  # Qt compiled resources
]

a = Analysis(
    [str(SRC / "bootv2.py")],
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
    upx=False,
    console=False,
    contents_directory="tinyui",
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="TinyUi",
)
