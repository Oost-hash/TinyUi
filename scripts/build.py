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

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
BUILD = ROOT / "build"
SPEC = ROOT / "TinyUi.spec"
EGG_INFO = ROOT / "src" / "TinyUi.egg-info"
APP_DIR = DIST / "TinyUi"
BUILD_ICON_SCRIPT = ROOT / "scripts" / "build_icon.py"

IS_WINDOWS = platform.system() == "Windows"
EXE_NAME = "TinyUi.exe" if IS_WINDOWS else "TinyUi"

USER_DIRS = {
    "config": ROOT / "data" / "config",
    "themes": ROOT / "src" / "assets" / "themes",
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


def _promote_internal_host() -> None:
    """Move the bundled TinyUi host package into its own top-level directory."""
    bundled_host = APP_DIR / "libs" / "plugins" / "tinyui"
    host_dst = APP_DIR / "tinyui"
    if not bundled_host.exists():
        raise RuntimeError(f"Bundled host package not found: {bundled_host}")
    if host_dst.exists():
        shutil.rmtree(host_dst)
    shutil.move(str(bundled_host), str(host_dst))


def _promote_external_plugins() -> None:
    """Move bundled external plugins into their top-level product directory."""
    bundled_plugins = APP_DIR / "libs" / "plugins"
    plugins_dst = APP_DIR / "plugins"
    if not bundled_plugins.exists():
        raise RuntimeError(f"Bundled plugins directory not found: {bundled_plugins}")
    if plugins_dst.exists():
        shutil.rmtree(plugins_dst)
    shutil.move(str(bundled_plugins), str(plugins_dst))


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


def _build_app_icon() -> None:
    """Ensure the logo PNG/ICO exist before packaging."""
    result = subprocess.run([sys.executable, str(BUILD_ICON_SCRIPT)], cwd=ROOT)
    if result.returncode != 0:
        raise RuntimeError(f"Icon build failed with code {result.returncode}")


def _print_structure() -> None:
    print(f"\nBuild complete: {APP_DIR}")
    print("Structure:")
    print("  TinyUi/")
    print(f"  +-- {EXE_NAME}")
    print("  +-- config/")
    print("  +-- data/")
    print("  +-- themes/")
    print("  +-- libs/")
    print("  +-- tinyui/")
    print("  +-- plugins/")


def build(*, skip_clean: bool) -> int:
    _clean_source_bytecode()
    _build_app_icon()

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
    _promote_internal_host()
    _promote_external_plugins()
    _ensure_user_dir("data")
    _print_structure()
    return 0


if __name__ == "__main__":
    args = _parse_args()
    raise SystemExit(build(skip_clean=args.skip_clean))
