#!/usr/bin/env python3
"""
TinyUi py2exe build script

Gebaseerd op TinyPedal's freeze_py2exe.py.
Strategie: kopieer tinyui/ naar tinypedal/, maak entry point,
en bouw vanuit tinypedal/ directory (net als TinyPedal zelf).
"""

import os
import shutil
import sys
from glob import glob
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent

# --- Stap 1: Prep - kopieer tinyui module en maak entry point ---

tinyui_src = PROJECT_ROOT / "tinyui"
tinyui_dst = PROJECT_ROOT / "tinypedal" / "tinyui"

if tinyui_dst.exists():
    shutil.rmtree(tinyui_dst)
shutil.copytree(tinyui_src, tinyui_dst)
print("-> tinyui/ gekopieerd naar tinypedal/tinyui/")

# Entry point: volgt TinyPedal's run.py patroon (sys.argv[0], niet __file__)
ENTRY_POINT = """\
import os
import sys

os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

from tinyui.main import run
sys.exit(run())
"""

entry_point_path = PROJECT_ROOT / "tinypedal" / "run_tinyui.py"
entry_point_path.write_text(ENTRY_POINT)
print("-> run_tinyui.py gemaakt")

# --- Stap 2: Wissel naar tinypedal/ en importeer (net als TinyPedal doet) ---

os.chdir(PROJECT_ROOT / "tinypedal")
sys.path.insert(0, str(PROJECT_ROOT / "tinypedal"))
sys.path.insert(0, str(PROJECT_ROOT))

from py2exe import freeze

from tinypedal import version_check
from tinypedal.const_app import PLATFORM
from tinyui.const_tinyui import APP_NAME, AUTHOR, VERSION

# --- Stap 3: Build configuratie (identiek aan TinyPedal) ---

PYTHON_PATH = sys.exec_prefix
DIST_FOLDER = str(PROJECT_ROOT / "dist")
APP_NAME_DIST = f"{DIST_FOLDER}/{APP_NAME}"

EXECUTABLE_SETTING = [
    {
        "script": "run_tinyui.py",
        "icon_resources": [(1, "images/icon.ico")],
        "dest_base": APP_NAME.lower(),
    }
]

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
    "docs/changelog.txt",
    "docs/customization.md",
    "docs/contributors.md",
]

LICENSES_FILES = glob("docs/licenses/*")

QT_PLATFORMS = [
    f"{PYTHON_PATH}/Lib/site-packages/PySide2/plugins/platforms/qwindows.dll",
]

QT_MEDIASERVICE = [
    f"{PYTHON_PATH}/Lib/site-packages/PySide2/plugins/mediaservice/dsengine.dll",
    f"{PYTHON_PATH}/Lib/site-packages/PySide2/plugins/mediaservice/wmfengine.dll",
]

BUILD_DATA_FILES = [
    ("", ["LICENSE.txt", "README.md"]),
    ("docs", DOCUMENT_FILES),
    ("docs/licenses", LICENSES_FILES),
    ("images", IMAGE_FILES),
    ("platforms", QT_PLATFORMS),
    ("mediaservice", QT_MEDIASERVICE),
]

INCLUDE_MODULES = [
    "tinypedal.module_info",
    "tinypedal.hotkey_control",
    "tinypedal.hotkey.command",
    "tinypedal.userfile.consumption_history",
    "tinypedal.userfile.driver_stats",
    "tinypedal.userfile.heatmap",
    "tinypedal.userfile.track_map",
    "tinypedal.userfile.track_notes",
]

BUILD_OPTIONS = {
    "dist_dir": APP_NAME_DIST,
    "includes": INCLUDE_MODULES,
    "excludes": EXCLUDE_MODULES,
    "optimize": 2,
    "compressed": 1,
}

BUILD_VERSION = {
    "version": VERSION.split("-")[0] if "-" in VERSION else VERSION,
    "description": APP_NAME,
    "copyright": f"Copyright (C) 2025 {AUTHOR}",
    "product_name": APP_NAME,
    "product_version": VERSION,
}

# --- Stap 4: Build ---

print(f"\nBuilding {APP_NAME} v{VERSION}...")
print(f"Platform: {PLATFORM.SYSTEM}")
print(f"Python:   {version_check.python()}")
print(f"Qt:       {version_check.qt()}")
print(f"PySide:   {version_check.pyside()}")

os.makedirs(DIST_FOLDER, exist_ok=True)
if os.path.exists(APP_NAME_DIST):
    shutil.rmtree(APP_NAME_DIST)

freeze(
    version_info=BUILD_VERSION,
    windows=EXECUTABLE_SETTING,
    options=BUILD_OPTIONS,
    data_files=BUILD_DATA_FILES,
    zipfile="lib/library.zip",
)

print("\n-> py2exe freeze klaar")

# --- Stap 5: PySide2 runtime DLLs kopiëren ---
# py2exe pakt de .pyd en Qt5*.dll maar mist de MSVC/OpenGL runtime DLLs
# die PySide2 meelevert in zijn eigen folder.

print("\nPySide2 runtime DLLs kopiëren...")
pyside2_path = Path(PYTHON_PATH) / "Lib" / "site-packages" / "PySide2"
lib_dir = Path(APP_NAME_DIST) / "lib"

for dll in pyside2_path.glob("*.dll"):
    dst = lib_dir / dll.name
    if not dst.exists():
        shutil.copy2(dll, dst)
        print(f"  + {dll.name}")

# --- Stap 6: Data folders ---

print("\nData folders toevoegen...")
dist_app_path = Path(APP_NAME_DIST)

for folder in ["brandlogo", "carsetups", "deltabest", "pacenotes",
               "trackmap", "tracknotes", "settings"]:
    src = PROJECT_ROOT / folder
    dst = dist_app_path / folder
    if src.exists():
        shutil.copytree(src, dst, dirs_exist_ok=True)
        print(f"  + {folder}/")
    else:
        dst.mkdir(exist_ok=True)
        print(f"  + {folder}/ (leeg)")

# --- Stap 7: Cleanup ---

print("\nCleanup...")
if tinyui_dst.exists():
    shutil.rmtree(tinyui_dst)
if entry_point_path.exists():
    entry_point_path.unlink()

print(f"\n{'=' * 50}")
print(f"RELEASE: dist/{APP_NAME}/")
print(f"{'=' * 50}")
