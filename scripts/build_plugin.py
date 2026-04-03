"""Build a compiled TinyUi plugin package from a manifest-driven source plugin."""

from __future__ import annotations

import argparse
import compileall
import hashlib
import py_compile
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

import tomllib

ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = ROOT / "src"
DEFAULT_DIST = ROOT / "dist" / "plugins"
DEFAULT_CONFIG_ROOT = ROOT / "data" / "config"

IGNORE_NAMES = {
    "__pycache__",
    ".git",
    ".github",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "tests",
}

IGNORE_SUFFIXES = {
    ".pyc",
    ".pyo",
    ".md",
    ".txt",
    ".sln",
    ".pyproj",
    ".bat",
    ".cmd",
    ".gitignore",
    ".gitmodules",
    ".pylintrc",
    ".requirements",
}

FROZEN_SOURCE_EXCLUDES = {"manifest.toml"}


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a TinyUi plugin package.")
    parser.add_argument("plugin_dir", help="Path to the source plugin directory")
    parser.add_argument("--output-dir", default=str(DEFAULT_DIST), help="Directory for built plugins")
    parser.add_argument("--clean", action="store_true", help="Remove the output plugin directory before building")
    parser.add_argument("--zip", action="store_true", help="Create a zip artifact next to the packaged directory")
    return parser.parse_args()


def _read_manifest(path: Path) -> dict:
    with path.open("rb") as f:
        return tomllib.load(f)


def _require_string(data: dict, key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Plugin manifest must define '{key}' as a non-empty string")
    return value


def _plugin_meta(data: dict, plugin_dir: Path) -> tuple[str, str, str]:
    plugin = data.get("plugin")
    if not isinstance(plugin, dict):
        raise ValueError("Plugin manifest must define a [plugin] table")
    plugin_id = _require_string(plugin, "id")
    plugin_type = _require_string(plugin, "type")
    version = _require_string(plugin, "version")
    if plugin_id != plugin_dir.name:
        raise ValueError(f"Manifest plugin id '{plugin_id}' must match directory name '{plugin_dir.name}'")
    return plugin_id, plugin_type, version


def _copytree_filtered(src: Path, dst: Path) -> None:
    def _ignore(directory: str, names: list[str]) -> set[str]:
        ignored: set[str] = set()
        for name in names:
            p = Path(directory) / name
            if name in IGNORE_NAMES or name in FROZEN_SOURCE_EXCLUDES:
                ignored.add(name)
                continue
            if p.is_file() and any(name.endswith(suffix) for suffix in IGNORE_SUFFIXES):
                ignored.add(name)
        return ignored

    shutil.copytree(src, dst, ignore=_ignore)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _runtime_archive_name(plugin_id: str) -> str:
    return f"{plugin_id}.pkg"


def _write_packaged_manifest(source_manifest: Path, target_manifest: Path) -> None:
    target_manifest.write_text(source_manifest.read_text(encoding="utf-8"), encoding="utf-8")


def _write_manifest_lock(
    path: Path,
    *,
    plugin_id: str,
    version: str,
    runtime_artifact: str,
    runtime_hash: str,
    config_defaults: list[str],
) -> None:
    lines = [
        f'plugin = "{plugin_id}"',
        f'version = "{version}"',
        'package_format = "compiled-v2"',
        f'runtime_artifact = "{runtime_artifact}"',
        f'runtime_sha256 = "{runtime_hash}"',
        "",
        "[config_defaults]",
        "items = [",
    ]
    lines.extend(f'  "{item}",' for item in config_defaults)
    lines.append("]")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _zip_dir(source_dir: Path, zip_path: Path) -> None:
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file in sorted(source_dir.rglob("*")):
            if file.is_file():
                zf.write(file, file.relative_to(source_dir))


def _build_runtime_package(plugin_dir: Path, artifact_path: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="tinyui-plugin-build-") as temp_dir_str:
        temp_dir = Path(temp_dir_str)
        source_root = temp_dir / "source"
        compiled_root = temp_dir / "compiled"

        _copytree_filtered(plugin_dir, source_root)
        compileall.compile_dir(
            str(source_root),
            quiet=1,
            force=True,
            legacy=False,
            optimize=0,
        )

        compiled_root.mkdir(parents=True, exist_ok=True)
        package_root = compiled_root / "plugins" / plugin_dir.name
        package_root.parent.mkdir(parents=True, exist_ok=True)

        plugins_init = SRC_ROOT / "plugins" / "__init__.py"
        if plugins_init.exists():
            py_compile.compile(
                str(plugins_init),
                cfile=str(package_root.parent / "__init__.pyc"),
                doraise=True,
            )

        for file in sorted(source_root.rglob("*")):
            if file.is_dir():
                continue
            rel = file.relative_to(source_root)
            if "__pycache__" in rel.parts and file.suffix == ".pyc":
                parent = rel.parent.parent if rel.parent.name == "__pycache__" else rel.parent
                compiled_name = file.name.split(".", 1)[0] + ".pyc"
                dst = package_root / parent / compiled_name
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file, dst)
                continue

            if file.suffix != ".py":
                dst = package_root / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file, dst)

        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        _zip_dir(compiled_root, artifact_path)


def build_plugin(plugin_dir: Path, output_dir: Path, *, clean: bool, create_zip: bool) -> Path:
    plugin_dir = plugin_dir.resolve()
    manifest_path = plugin_dir / "manifest.toml"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Missing manifest.toml in {plugin_dir}")

    data = _read_manifest(manifest_path)
    plugin_id, _plugin_type, version = _plugin_meta(data, plugin_dir)
    package_dir = output_dir / plugin_id

    if clean and package_dir.exists():
        shutil.rmtree(package_dir)

    runtime_dir = package_dir / "runtime"
    internal_dir = package_dir / "_internal"
    config_defaults_dir = package_dir / "config" / "defaults"

    package_dir.mkdir(parents=True, exist_ok=True)
    runtime_dir.mkdir(parents=True, exist_ok=True)
    internal_dir.mkdir(parents=True, exist_ok=True)

    runtime_artifact = runtime_dir / _runtime_archive_name(plugin_id)
    _build_runtime_package(plugin_dir, runtime_artifact)
    _write_packaged_manifest(manifest_path, internal_dir / "manifest.toml")

    config_defaults: list[str] = []
    source_defaults_dir = plugin_dir / "config" / "defaults"
    if not source_defaults_dir.exists():
        source_defaults_dir = DEFAULT_CONFIG_ROOT / plugin_id
    if source_defaults_dir.exists():
        config_defaults_dir.mkdir(parents=True, exist_ok=True)
        for file in sorted(source_defaults_dir.glob("*.json")):
            shutil.copy2(file, config_defaults_dir / file.name)
            config_defaults.append(file.name)

    _write_manifest_lock(
        package_dir / "manifest.lock",
        plugin_id=plugin_id,
        version=version,
        runtime_artifact=f"runtime/{runtime_artifact.name}",
        runtime_hash=_sha256(runtime_artifact),
        config_defaults=config_defaults,
    )

    if create_zip:
        zip_path = output_dir / f"{plugin_id}-{version}.zip"
        if zip_path.exists():
            zip_path.unlink()
        _zip_dir(package_dir, zip_path)

    return package_dir


def main() -> int:
    args = _parse_args()
    plugin_dir = Path(args.plugin_dir)
    output_dir = Path(args.output_dir)
    package_dir = build_plugin(plugin_dir, output_dir, clean=args.clean, create_zip=args.zip)
    print(f"Built plugin package: {package_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
