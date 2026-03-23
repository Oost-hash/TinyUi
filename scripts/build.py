"""Build standalone app with PyInstaller — Windows and Linux."""

import platform
import shutil
import subprocess
import sys
from pathlib import Path

ROOT    = Path(__file__).resolve().parents[1]   # scripts/ -> repo root
ENTRY   = ROOT / "src" / "tinyui" / "main.py"
DIST    = ROOT / "dist"
BUILD   = ROOT / "build"
SPEC    = ROOT / "TinyUi.spec"
EGG_INFO = ROOT / "src" / "tinyui.egg-info"

IS_WINDOWS = platform.system() == "Windows"
IS_LINUX   = platform.system() == "Linux"

EXE_NAME = "TinyUi.exe" if IS_WINDOWS else "TinyUi"
APP_DIR  = DIST / "TinyUi"

ICON = (
    ROOT / "src" / "tinyui" / "images" / "icon.ico"
    if IS_WINDOWS else
    ROOT / "src" / "tinyui" / "images" / "icon.png"
)

# User-facing folders to place next to the executable
USER_DIRS = {
    "config":  ROOT / "data" / "plugin-config",
    "themes":  ROOT / "src" / "tinyui" / "themes",
    "plugins": ROOT / "src" / "plugins",
}


def clean():
    """Remove build artifacts."""
    for path in (DIST, BUILD, SPEC, EGG_INFO):
        if path.is_dir():
            shutil.rmtree(path)
            print(f"Removed {path}")
        elif path.is_file():
            path.unlink()
            print(f"Removed {path}")


def _copy_user_dir(name: str, src: Path):
    """Copy a user-facing directory next to the exe."""
    dst = APP_DIR / name
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))


def build():
    clean()

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", "TinyUi",
        "--onedir",
        "--windowed",
        "--contents-directory", "lib",
        "--collect-all", "tinycore",
        "--collect-all", "plugins",
        "--collect-all", "tinyui",
        "--paths", str(ROOT / "src"),
        "--distpath", str(DIST),
        "--workpath", str(BUILD),
        "--specpath", str(ROOT),
        "--noconfirm",
    ]

    if ICON.exists():
        cmd.extend(["--icon", str(ICON)])

    cmd.append(str(ENTRY))

    print(f"Building TinyUi for {platform.system()} ...")
    result = subprocess.run(cmd)

    # Remove intermediate build artifacts
    for path in (BUILD, SPEC, EGG_INFO):
        if path.is_dir():
            shutil.rmtree(path)
        elif path.is_file():
            path.unlink()

    if result.returncode == 0:
        for name, src in USER_DIRS.items():
            if src.exists():
                _copy_user_dir(name, src)

        print(f"\nBuild complete: {APP_DIR}")
        print("Structure:")
        print("  TinyUi/")
        print(f"  +-- {EXE_NAME}")
        print("  +-- config/")
        print("  +-- themes/")
        print("  +-- plugins/")
        print("  +-- lib/")
    else:
        print(f"\nBuild failed with code {result.returncode}")

    return result.returncode


if __name__ == "__main__":
    sys.exit(build())
