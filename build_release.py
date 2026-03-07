#!/usr/bin/env python3
"""
TinyUi py2exe build script

Based on TinyPedal's freeze_py2exe.py.
Strategy: copy tinyui/ into tinypedal/, create entry point,
and build from the tinypedal/ directory (same as TinyPedal itself).

Produces two outputs:
  dist/TinyUi/        - full build with TinyPedal data folders
  dist/TinyUi-minimal/ - drop-in build for existing TinyPedal installs
"""

import os
import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
TINYUI_SRC = PROJECT_ROOT / "tinyui"

# Data folders to include in the full build (removed in minimal)
DATA_FOLDERS = [
    "brandlogo",
    "carsetups",
    "deltabest",
    "pacenotes",
    "trackmap",
    "tracknotes",
    "settings",
]

# Entry point: follows TinyPedal's run.py pattern (sys.argv[0], not __file__)
ENTRY_POINT = """\
import os
import sys

os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

from tinyui.main import run
sys.exit(run())
"""

EXCLUDE_MODULES = [
    "difflib",
    "pdb",
    "venv",
    "tkinter",
    "curses",
    "distutils",
    "lib2to3",
    "unittest",
    "xmlrpc",
    "multiprocessing",
]

IMAGE_FILES = [
    "images/CC-BY-SA-4.0.txt",
    "images/icon_compass.png",
    "images/icon_instrument.png",
    "images/icon_steering_wheel.png",
    "images/icon_weather.png",
    "images/icon.png",
]

DOCUMENT_FILES = [
    str(PROJECT_ROOT / "docs" / "changelog.md"),
    "docs/customization.md",
    "docs/contributors.md",
]

THEME_FILES = [
    str(p) for p in (PROJECT_ROOT / "tinyui" / "themes").glob("*.json")
]

TINYUI_IMAGE_FILES = [
    str(p) for p in (PROJECT_ROOT / "tinyui" / "images").glob("*.png")
] + [
    str(p) for p in (PROJECT_ROOT / "tinyui" / "images").glob("*.ico")
]


# Files to exclude from production builds (dev-only tooling)
EXCLUDE_FROM_BUILD = {"generate_adapters.py"}


def discover_tinyui_modules():
    """Auto-discover all tinyui Python modules from the filesystem."""
    modules = []
    for py_file in TINYUI_SRC.rglob("*.py"):
        if py_file.name in EXCLUDE_FROM_BUILD:
            continue
        rel = py_file.relative_to(PROJECT_ROOT)
        if rel.stem == "__init__":
            module = str(rel.parent).replace(os.sep, ".")
        else:
            module = str(rel.with_suffix("")).replace(os.sep, ".")
        modules.append(module)
    modules.sort()
    return modules


def detect_pyside():
    """Detect installed PySide version and return (package_name, site_path)."""
    python_path = Path(sys.exec_prefix)
    site_packages = python_path / "Lib" / "site-packages"
    for name in ("PySide6", "PySide2"):
        pyside_path = site_packages / name
        if pyside_path.exists():
            return name, pyside_path
    sys.exit("ERROR: No PySide2 or PySide6 installation found")


def build():
    """Run the full build process."""
    pyside_name, pyside_path = detect_pyside()

    # -- Step 1: Copy tinyui module into tinypedal/ and create entry point --

    tinyui_dst = PROJECT_ROOT / "tinypedal" / "tinyui"
    entry_point_path = PROJECT_ROOT / "tinypedal" / "run_tinyui.py"

    if tinyui_dst.exists():
        shutil.rmtree(tinyui_dst)
    shutil.copytree(TINYUI_SRC, tinyui_dst)

    # Remove dev-only files from the build copy
    for dev_file in ("generate_adapters.py", "manifest.json"):
        dev_path = tinyui_dst / "backend" / dev_file
        if dev_path.exists():
            dev_path.unlink()
    print("-> tinyui/ copied to tinypedal/tinyui/ (dev files excluded)")

    entry_point_path.write_text(ENTRY_POINT)
    print("-> run_tinyui.py created")

    # -- Step 1b: Generate backend adapters from manifest --

    from tinyui.backend.generate_adapters import generate
    generate()
    print("-> Backend adapters generated")

    # -- Step 2: Switch to tinypedal/ and import (same as TinyPedal does) --

    os.chdir(PROJECT_ROOT / "tinypedal")

    # tinypedal/ (submodule root) must come before PROJECT_ROOT on sys.path,
    # otherwise Python finds the tinypedal/ directory as a namespace package
    # (no __init__.py) instead of the real tinypedal/tinypedal/ package.
    project_root_str = str(PROJECT_ROOT)
    sys.path[:] = [p for p in sys.path if p != project_root_str and p != "."]
    sys.path.insert(0, str(PROJECT_ROOT / "tinypedal"))
    sys.path.insert(1, project_root_str)

    from glob import glob as globfiles

    from py2exe import freeze
    from tinypedal.const_app import PLATFORM

    from tinypedal import version_check
    from tinyui.const_tinyui import APP_NAME, AUTHOR
    from tinyui.version import __version__ as VERSION

    # -- Step 3: Build configuration --

    python_path = sys.exec_prefix
    dist_folder = str(PROJECT_ROOT / "dist")
    app_name_dist = f"{dist_folder}/{APP_NAME}"

    executable_setting = [
        {
            "script": "run_tinyui.py",
            "icon_resources": [(1, "tinyui/images/icon.ico")],
            "dest_base": APP_NAME.lower(),
        }
    ]

    licenses_files = globfiles("docs/licenses/*")

    qt_platforms = [
        f"{python_path}/Lib/site-packages/{pyside_name}/plugins/platforms/qwindows.dll",
    ]

    qt_mediaservice = [
        f"{python_path}/Lib/site-packages/{pyside_name}/plugins/mediaservice/dsengine.dll",
        f"{python_path}/Lib/site-packages/{pyside_name}/plugins/mediaservice/wmfengine.dll",
    ]

    # Tinypedal modules that py2exe doesn't pick up automatically
    tinypedal_includes = [
        "tinypedal.module_info",
        "tinypedal.hotkey_control",
        "tinypedal.hotkey.command",
        "tinypedal.userfile.consumption_history",
        "tinypedal.userfile.driver_stats",
        "tinypedal.userfile.heatmap",
        "tinypedal.userfile.track_map",
        "tinypedal.userfile.track_notes",
    ]

    tinyui_modules = discover_tinyui_modules()
    print(f"-> Discovered {len(tinyui_modules)} tinyui modules")

    include_modules = tinypedal_includes + tinyui_modules

    build_data_files = [
        ("", ["LICENSE.txt", "README.md"]),
        ("docs", DOCUMENT_FILES),
        ("docs/licenses", licenses_files),
        ("images", IMAGE_FILES),
        ("tinyui/themes", THEME_FILES),
        ("tinyui/images", TINYUI_IMAGE_FILES),
        ("platforms", qt_platforms),
        ("mediaservice", qt_mediaservice),
    ]

    build_options = {
        "dist_dir": app_name_dist,
        "includes": include_modules,
        "excludes": EXCLUDE_MODULES,
        "optimize": 2,
        "compressed": 1,
    }

    build_version = {
        "version": VERSION.split("-")[0] if "-" in VERSION else VERSION,
        "description": APP_NAME,
        "copyright": f"Copyright (C) 2025 {AUTHOR}",
        "product_name": APP_NAME,
        "product_version": VERSION,
    }

    # -- Step 4: Build --

    print(f"\nBuilding {APP_NAME} v{VERSION}...")
    print(f"Platform: {PLATFORM.SYSTEM}")
    print(f"Python:   {version_check.python()}")
    print(f"Qt:       {version_check.qt()}")
    print(f"PySide:   {version_check.pyside()} ({pyside_name})")

    os.makedirs(dist_folder, exist_ok=True)
    if os.path.exists(app_name_dist):
        shutil.rmtree(app_name_dist)

    freeze(
        version_info=build_version,
        windows=executable_setting,
        options=build_options,
        data_files=build_data_files,
        zipfile="tinyui_lib/library.zip",
    )

    print("\n-> py2exe freeze complete")

    # -- Step 5: Copy PySide runtime DLLs --

    print(f"\nCopying {pyside_name} runtime DLLs...")
    lib_dir = Path(app_name_dist) / "tinyui_lib"

    for dll in pyside_path.glob("*.dll"):
        dst = lib_dir / dll.name
        if not dst.exists():
            shutil.copy2(dll, dst)
            print(f"  + {dll.name}")

    # -- Step 6: Data folders (full build) --

    print("\nAdding data folders...")
    dist_app_path = Path(app_name_dist)

    for folder in DATA_FOLDERS:
        src = PROJECT_ROOT / folder
        dst = dist_app_path / folder
        if src.exists():
            shutil.copytree(src, dst, dirs_exist_ok=True)
            print(f"  + {folder}/")
        else:
            dst.mkdir(exist_ok=True)
            print(f"  + {folder}/ (empty)")

    # -- Step 7: Cleanup temp files --

    print("\nCleanup...")
    if tinyui_dst.exists():
        shutil.rmtree(tinyui_dst)
    if entry_point_path.exists():
        entry_point_path.unlink()

    print(f"\n{'=' * 50}")
    print(f"RELEASE: dist/{APP_NAME}/")
    print(f"{'=' * 50}")

    # -- Step 8: Minimal drop-in build --
    # Structure mirrors TinyPedal so files merge cleanly when dropped in.
    # TinyUi-specific files go under tinyui/ to avoid overwriting TinyPedal's.

    print("\n--- Minimal drop-in build ---")

    minimal_name = f"{APP_NAME}-minimal"
    minimal_path = PROJECT_ROOT / "dist" / minimal_name

    if minimal_path.exists():
        shutil.rmtree(minimal_path)

    shutil.copytree(app_name_dist, minimal_path)
    print(f"-> Build copied to {minimal_name}/")

    # Remove everything TinyPedal already provides
    remove_folders = DATA_FOLDERS + ["images", "docs", "platforms", "mediaservice", "lib"]
    removed = []
    for folder in remove_folders:
        folder_path = minimal_path / folder
        if folder_path.exists():
            shutil.rmtree(folder_path)
            removed.append(folder)

    # Remove root LICENSE/README (TinyPedal has its own)
    for root_file in ("LICENSE.txt", "README.md"):
        file_path = minimal_path / root_file
        if file_path.exists():
            file_path.unlink()
            removed.append(root_file)

    if removed:
        print(f"  - Removed: {', '.join(removed)}")

    # Add TinyUi-specific docs under tinyui/ so they don't clash
    tinyui_dir = minimal_path / "tinyui"
    tinyui_dir.mkdir(exist_ok=True)

    # Copy TinyUi docs
    tinyui_docs_dir = tinyui_dir / "docs"
    tinyui_docs_dir.mkdir(exist_ok=True)
    for doc in DOCUMENT_FILES:
        src = PROJECT_ROOT / "tinypedal" / doc
        if src.exists():
            shutil.copy2(src, tinyui_docs_dir / src.name)
    print(f"  + tinyui/docs/")

    # Copy TinyUi license and readme
    for root_file in ("LICENSE.txt", "README.md"):
        src = PROJECT_ROOT / root_file
        if src.exists():
            shutil.copy2(src, tinyui_dir / root_file)
    print(f"  + tinyui/LICENSE.txt, README.md")

    remaining = sorted(f.name for f in minimal_path.iterdir())
    print(f"  = Contents: {', '.join(remaining)}")

    print(f"\n{'=' * 50}")
    print(f"MINIMAL: dist/{minimal_name}/")
    print(f"{'=' * 50}")


if __name__ == "__main__":
    build()
