"""Build standalone .exe with PyInstaller."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
ENTRY = ROOT / "src" / "tinyui" / "main.py"
DIST = ROOT / "dist"
ICON = ROOT / "src" / "tinyui" / "images" / "icon.ico"

def build():
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", "TinyUi",
        "--onedir",
        "--windowed",
        # Packages to collect
        "--collect-all", "tinycore",
        "--collect-all", "plugins",
        "--collect-all", "tinyui",
        # Paths
        "--paths", str(ROOT / "src"),
        "--distpath", str(DIST),
        "--workpath", str(ROOT / "build"),
        "--specpath", str(ROOT),
        # Overwrite
        "--noconfirm",
    ]

    # Add icon if it exists
    if ICON.exists():
        cmd.extend(["--icon", str(ICON)])

    cmd.append(str(ENTRY))

    print(f"Building TinyUi .exe ...")
    print(f"Entry: {ENTRY}")
    print(f"Dist:  {DIST}")
    result = subprocess.run(cmd)
    if result.returncode == 0:
        print(f"\nBuild complete: {DIST / 'TinyUi'}")
    else:
        print(f"\nBuild failed with code {result.returncode}")
    return result.returncode

if __name__ == "__main__":
    sys.exit(build())
