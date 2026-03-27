"""Build the TinyUi app distribution and optionally package first-party plugins."""

from __future__ import annotations

import argparse
import platform
import shutil
import subprocess
import sys
from pathlib import Path

ROOT    = Path(__file__).resolve().parents[1]   # scripts/ -> repo root
ENTRY   = ROOT / "src" / "tinyui_boot.py"
DIST    = ROOT / "dist"
BUILD   = ROOT / "build"
SPEC    = ROOT / "TinyUi.spec"
EGG_INFO = ROOT / "src" / "tinyui.egg-info"
PLUGIN_BUILD_SCRIPT = ROOT / "scripts" / "build_plugin.py"

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
}


def _clean_source_bytecode() -> None:
    """Remove cached Python bytecode from the source tree before packaging."""
    src_root = ROOT / "src"
    if not src_root.exists():
        return

    for cache_dir in sorted(src_root.rglob("__pycache__")):
        if cache_dir.is_dir():
            shutil.rmtree(cache_dir)
            print(f"Removed {cache_dir}")

    for pyc_file in sorted(src_root.rglob("*.pyc")):
        if pyc_file.is_file():
            pyc_file.unlink()
            print(f"Removed {pyc_file}")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the TinyUi app distribution.")
    parser.add_argument("--skip-clean", action="store_true", help="Keep existing dist/build folders before running")
    parser.add_argument("--app-only", action="store_true", help="Build only the main program and skip plugin packaging")
    parser.add_argument("--plugins-only", action="store_true", help="Package plugins into the app dist without running PyInstaller")
    parser.add_argument("--with-devtools", action="store_true", help="Include the optional tinydevtools package in the built app")
    return parser.parse_args()


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


def _build_packaged_plugins() -> None:
    """Build packaged plugins into the app distribution."""
    _clean_source_bytecode()
    plugins_src = ROOT / "src" / "plugins"
    plugins_dst = APP_DIR / "plugins"
    print(f"Packaging plugins into {plugins_dst} ...")
    if plugins_dst.exists():
        shutil.rmtree(plugins_dst)
    plugins_dst.mkdir(parents=True, exist_ok=True)

    for manifest_path in sorted(plugins_src.glob("*/plugin.toml")):
        print(f"  - {manifest_path.parent.name}")
        cmd = [
            sys.executable,
            str(PLUGIN_BUILD_SCRIPT),
            str(manifest_path.parent),
            "--output-dir",
            str(plugins_dst),
            "--clean",
        ]
        result = subprocess.run(cmd)
        if result.returncode != 0:
            raise RuntimeError(
                f"Plugin build failed for '{manifest_path.parent.name}' with code {result.returncode}"
            )


def _pyinstaller_cmd(*, with_devtools: bool) -> list[str]:
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", "TinyUi",
        "--onedir",
        "--windowed",
        "--contents-directory", "_runtime",
        "--collect-all", "tinycore",
        "--collect-all", "tinyui",
        "--collect-all", "tinyui_schema",
        "--collect-all", "tinywidgets",
        "--paths", str(ROOT / "src"),
        "--distpath", str(DIST),
        "--workpath", str(BUILD),
        "--specpath", str(ROOT),
        "--noconfirm",
    ]

    if ICON.exists():
        cmd.extend(["--icon", str(ICON)])

    if with_devtools:
        cmd.extend(["--collect-all", "tinydevtools"])

    cmd.append(str(ENTRY))
    return cmd


def _print_structure() -> None:
    print(f"\nBuild complete: {APP_DIR}")
    print("Structure:")
    print("  TinyUi/")
    print(f"  +-- {EXE_NAME}")
    print("  +-- config/")
    print("  +-- themes/")
    print("  +-- plugins/")
    print("  +-- _runtime/")


def build(*, skip_clean: bool, app_only: bool, plugins_only: bool, with_devtools: bool) -> int:
    _clean_source_bytecode()

    if plugins_only:
        if not APP_DIR.exists():
            print(f"Build failed: app directory does not exist yet: {APP_DIR}")
            return 1
        _build_packaged_plugins()
        _print_structure()
        return 0

    if not skip_clean:
        clean()

    print(f"Building TinyUi for {platform.system()} ...")
    result = subprocess.run(_pyinstaller_cmd(with_devtools=with_devtools))

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
        if not app_only:
            _build_packaged_plugins()
        _print_structure()
    else:
        print(f"\nBuild failed with code {result.returncode}")

    return result.returncode


if __name__ == "__main__":
    args = _parse_args()
    if args.app_only and args.plugins_only:
        print("Build failed: --app-only and --plugins-only cannot be used together")
        raise SystemExit(1)
    sys.exit(
        build(
            skip_clean=args.skip_clean,
            app_only=args.app_only,
            plugins_only=args.plugins_only,
            with_devtools=args.with_devtools,
        )
    )
