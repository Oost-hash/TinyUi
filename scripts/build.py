"""Build the TinyUi application distribution from the fixed PyInstaller spec."""

from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path

from build_plugin import build_plugin as build_compiled_plugin

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
BUILD = ROOT / "build"
SPEC = ROOT / "TinyUi.spec"
EGG_INFO = ROOT / "src" / "TinyUi.egg-info"
APP_DIR = DIST / "TinyUi"
BUILD_ASSETS_SCRIPT = ROOT / "scripts" / "build_assets.py"

IS_WINDOWS = platform.system() == "Windows"
EXE_NAME = "TinyUi.exe" if IS_WINDOWS else "TinyUi"

USER_DIRS = {
    "config": ROOT / "data" / "config",
    "themes": ROOT / "assets" / "themes",
}


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the TinyUi app distribution.")
    parser.add_argument("--skip-clean", action="store_true", help="Keep existing dist/build folders before running")
    return parser.parse_args()


def _clean_source_bytecode() -> None:
    """Remove cached Python bytecode from the source tree before packaging."""
    src_root = ROOT / "src"
    if not src_root.exists():
        return

    for cache_dir in sorted(src_root.rglob("__pycache__")):
        if cache_dir.is_dir():
            shutil.rmtree(cache_dir)

    for pyc_file in sorted(src_root.rglob("*.pyc")):
        if pyc_file.is_file():
            pyc_file.unlink()


def clean() -> None:
    """Remove build artifacts."""
    for path in (DIST, BUILD, EGG_INFO):
        if path.is_dir():
            _remove_tree(path)
            print(f"Removed {path}")
        elif path.is_file():
            path.unlink()
            print(f"Removed {path}")


def _handle_remove_error(func, target: str, exc_info) -> None:
    """Retry removals on Windows after clearing read-only bits."""
    del exc_info
    os.chmod(target, 0o700)
    func(target)


def _remove_tree(path: Path, retries: int = 5, delay: float = 0.5) -> None:
    last_error: OSError | None = None
    for attempt in range(retries):
        try:
            shutil.rmtree(path, onexc=_handle_remove_error)
            return
        except OSError as exc:
            last_error = exc
            if attempt == retries - 1:
                break
            time.sleep(delay)
    if last_error is not None:
        raise last_error


def _copy_user_dir(name: str, src: Path) -> None:
    """Copy a user-facing directory next to the executable."""
    dst = APP_DIR / name
    if dst.exists():
        shutil.rmtree(dst)
    if src.exists():
        shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    else:
        dst.mkdir(parents=True, exist_ok=True)


def _build_external_plugins() -> None:
    """Build external plugins into packaged distribution directories."""
    source_plugins = ROOT / "src" / "plugins"
    plugins_dst = APP_DIR / "plugins"
    if plugins_dst.exists():
        shutil.rmtree(plugins_dst)
    plugins_dst.mkdir(parents=True, exist_ok=True)
    for plugin_dir in sorted(source_plugins.iterdir()):
        if not plugin_dir.is_dir() or plugin_dir.name in {"tinyui", "__pycache__"}:
            continue
        build_compiled_plugin(plugin_dir, plugins_dst, clean=True, create_zip=False)


def _ensure_user_dir(name: str) -> None:
    """Create a canonical user-facing directory next to the executable."""
    (APP_DIR / name).mkdir(parents=True, exist_ok=True)


def _pyinstaller_cmd() -> list[str]:
    return [
        sys.executable,
        "-m",
        "PyInstaller",
        str(SPEC),
        "--distpath",
        str(DIST),
        "--workpath",
        str(BUILD),
        "--noconfirm",
    ]


def _build_assets() -> None:
    """Prepare generated and synced assets before packaging."""
    result = subprocess.run([sys.executable, str(BUILD_ASSETS_SCRIPT)], cwd=ROOT)
    if result.returncode != 0:
        raise RuntimeError(f"Asset build failed with code {result.returncode}")


def _print_structure() -> None:
    print(f"\nBuild complete: {APP_DIR}")
    print("Structure:")
    print("  TinyUi/")
    print(f"  +-- {EXE_NAME}")
    print("  +-- config/")
    print("  +-- data/")
    print("  +-- themes/")
    print("  +-- tinyui/")
    print("  +-- plugins/")


def build(*, skip_clean: bool) -> int:
    _clean_source_bytecode()
    _build_assets()

    if not skip_clean:
        clean()

    print(f"Building TinyUi for {platform.system()} ...")
    result = subprocess.run(_pyinstaller_cmd(), cwd=ROOT)

    if EGG_INFO.exists():
        shutil.rmtree(EGG_INFO)

    if result.returncode != 0:
        print(f"\nBuild failed with code {result.returncode}")
        return result.returncode

    for name, src in USER_DIRS.items():
        _copy_user_dir(name, src)
    _build_external_plugins()
    _ensure_user_dir("data")
    _print_structure()
    return 0


if __name__ == "__main__":
    args = _parse_args()
    raise SystemExit(build(skip_clean=args.skip_clean))
