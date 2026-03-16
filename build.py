"""Build standalone .exe with PyInstaller."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
ENTRY = ROOT / "src" / "tinyui" / "main.py"
DIST = ROOT / "dist"
APP_DIR = DIST / "TinyUi"
BUILD = ROOT / "build"
ICON = ROOT / "src" / "tinyui" / "images" / "icon.ico"
SPEC = ROOT / "TinyUi.spec"
EGG_INFO = ROOT / "src" / "tinyui.egg-info"

# User-facing folders to place next to exe
USER_DIRS = {
    "config": ROOT / "data" / "plugin-config",
    "themes": ROOT / "src" / "tinyui" / "themes",
    "images": ROOT / "src" / "tinyui" / "images",
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
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns(
        "__pycache__", "*.pyc",
    ))


def build():
    clean()

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", "TinyUi",
        "--onedir",
        "--windowed",
        # Put runtime in lib/
        "--contents-directory", "lib",
        # Packages to collect
        "--collect-all", "tinycore",
        "--collect-all", "plugins",
        "--collect-all", "tinyui",
        # Paths
        "--paths", str(ROOT / "src"),
        "--distpath", str(DIST),
        "--workpath", str(BUILD),
        "--specpath", str(ROOT),
        # Overwrite
        "--noconfirm",
    ]

    if ICON.exists():
        cmd.extend(["--icon", str(ICON)])

    cmd.append(str(ENTRY))

    print("Building TinyUi .exe ...")
    result = subprocess.run(cmd)

    # Clean up build artifacts, keep only dist
    for path in (BUILD, SPEC, EGG_INFO):
        if path.is_dir():
            shutil.rmtree(path)
        elif path.is_file():
            path.unlink()

    if result.returncode == 0:
        # Copy user-facing dirs next to exe
        for name, src in USER_DIRS.items():
            if src.exists():
                _copy_user_dir(name, src)

        print(f"\nBuild complete: {APP_DIR}")
        print("Structure:")
        print("  TinyUi/")
        print("  ├── TinyUi.exe")
        print("  ├── config/")
        print("  ├── themes/")
        print("  ├── images/")
        print("  ├── plugins/")
        print("  └── lib/")
    else:
        print(f"\nBuild failed with code {result.returncode}")
    return result.returncode


if __name__ == "__main__":
    sys.exit(build())
