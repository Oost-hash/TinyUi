"""Build a TinyUi plugin package from a source plugin directory.

MVP goals:
- validate a legacy source plugin directory
- assemble the future packaged layout
- bundle runtime code into runtime/<name>.pkg
- copy user-facing widget and editor files plus config defaults
- write an internal plugin.toml for the packaged shape
- optionally create a zip artifact
"""

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
DEFAULT_CONFIG_ROOT = ROOT / "data" / "plugin-config"

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
USER_FACING_RUNTIME_EXCLUDES = {"plugin.toml", "widgets.toml", "editors.toml"}


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


def _validate_runtime_source(data: dict) -> tuple[str, str]:
    if "logic" in data:
        section_name = "logic"
    elif "provider" in data:
        section_name = "provider"
    else:
        raise ValueError("Plugin manifest must define either [logic] or [provider]")

    section = data[section_name]
    if not isinstance(section, dict):
        raise ValueError(f"Manifest section [{section_name}] must be a table")

    module = section.get("module")
    class_name = section.get("class")
    if not isinstance(module, str) or not module.strip():
        raise ValueError(f"Manifest section [{section_name}] must define 'module'")
    if not isinstance(class_name, str) or not class_name.strip():
        raise ValueError(f"Manifest section [{section_name}] must define 'class'")
    return module, class_name


def _copytree_filtered(src: Path, dst: Path) -> None:
    def _ignore(directory: str, names: list[str]) -> set[str]:
        ignored: set[str] = set()
        for name in names:
            p = Path(directory) / name
            if name in IGNORE_NAMES:
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


def _runtime_archive_name(plugin_name: str) -> str:
    return f"{plugin_name}.pkg"


def _runtime_section(data: dict, plugin_name: str) -> str:
    entry_module, entry_class = _validate_runtime_source(data)

    return (
        "[runtime]\n"
        'kind = "compiled"\n'
        f'entry_module = "{entry_module}"\n'
        f'entry_class = "{entry_class}"\n'
        f'artifact = "runtime/{_runtime_archive_name(plugin_name)}"\n'
    )


def _format_string_list(values: list[str]) -> str:
    if not values:
        return "[]"
    lines = ["["]
    lines.extend(f'  "{value}",' for value in values)
    lines.append("]")
    return "\n".join(lines)


def _build_packaged_manifest(
    data: dict,
    plugin_name: str,
    widget_files: list[tuple[str, str]],
    editor_files: list[tuple[str, str]],
    config_defaults: list[Path],
) -> str:
    lines: list[str] = [
        f'name = "{data["name"]}"',
        f'type = "{data["type"]}"',
        f'version = "{data["version"]}"',
        'api_version = "1"',
        'package_format = "compiled-v1"',
        "",
    ]

    requires = data.get("requires", [])
    exports = data.get("exports", [])
    if requires:
        lines.extend(["requires = " + _format_string_list(requires), ""])
    if exports:
        lines.extend(["exports = " + _format_string_list(exports), ""])

    if "logic" in data:
        lines.extend(
            [
                "[logic]",
                f'module = "{data["logic"]["module"]}"',
                f'class = "{data["logic"]["class"]}"',
                "",
            ]
        )

    if "provider" in data:
        lines.extend(
            [
                "[provider]",
                f'module = "{data["provider"]["module"]}"',
                f'class = "{data["provider"]["class"]}"',
                "",
            ]
        )

    lines.append(_runtime_section(data, plugin_name).rstrip())
    lines.append("")

    if any(src == "widgets/widgets.toml" for src, _ in widget_files):
        lines.extend(["[widgets]", 'file = "widgets/widgets.toml"', ""])

    if any(src == "editors/editors.toml" for src, _ in editor_files):
        lines.extend(["[editors]", 'file = "editors/editors.toml"', ""])

    lines.extend(["[user_files]", "preserve_user_files = true", ""])

    for src, target in [*widget_files, *editor_files]:
        lines.extend(
            [
                "[[user_files.files]]",
                f'source = "{src}"',
                f'target = "{target}"',
                'kind = "manifest"',
                "",
            ]
        )

    for cfg in config_defaults:
        lines.extend(
            [
                "[[user_files.files]]",
                f'source = "config/defaults/{cfg.name}"',
                f'target = "config/{plugin_name}/{cfg.name}"',
                'kind = "default-config"',
                "copy_if_missing = true",
                "",
            ]
        )

    return "\n".join(lines).rstrip() + "\n"


def _write_manifest_lock(
    path: Path,
    *,
    plugin_name: str,
    version: str,
    runtime_artifact: str,
    runtime_hash: str,
    user_files: list[str],
) -> None:
    lines = [
        f'plugin = "{plugin_name}"',
        f'version = "{version}"',
        'package_format = "compiled-v1"',
        f'runtime_artifact = "{runtime_artifact}"',
        f'runtime_sha256 = "{runtime_hash}"',
        "",
        "[user_files]",
        "items = [",
    ]
    lines.extend(f'  "{item}",' for item in user_files)
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
            if rel.name in USER_FACING_RUNTIME_EXCLUDES:
                continue
            if rel.parts and rel.parts[0] in {"ui", "config"}:
                continue
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
    manifest_path = plugin_dir / "plugin.toml"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Missing plugin.toml in {plugin_dir}")

    data = _read_manifest(manifest_path)
    plugin_name = _require_string(data, "name")
    _require_string(data, "type")
    _require_string(data, "version")
    _validate_runtime_source(data)
    package_dir = output_dir / plugin_name

    if clean and package_dir.exists():
        shutil.rmtree(package_dir)

    runtime_dir = package_dir / "runtime"
    widgets_dir = package_dir / "widgets"
    editors_dir = package_dir / "editors"
    internal_dir = package_dir / "_internal"
    config_defaults_dir = package_dir / "config" / "defaults"

    package_dir.mkdir(parents=True, exist_ok=True)
    runtime_dir.mkdir(parents=True, exist_ok=True)
    internal_dir.mkdir(parents=True, exist_ok=True)

    runtime_artifact = runtime_dir / _runtime_archive_name(plugin_name)
    _build_runtime_package(plugin_dir, runtime_artifact)

    widget_files: list[tuple[str, str]] = []
    editor_files: list[tuple[str, str]] = []
    widgets_src = plugin_dir / "widgets" / "widgets.toml"
    editors_src = plugin_dir / "editors" / "editors.toml"
    if widgets_src.exists():
        widgets_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(widgets_src, widgets_dir / "widgets.toml")
        widget_files.append(("widgets/widgets.toml", f"plugins/{plugin_name}/widgets/widgets.toml"))
    if editors_src.exists():
        editors_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(editors_src, editors_dir / "editors.toml")
        editor_files.append(("editors/editors.toml", f"plugins/{plugin_name}/editors/editors.toml"))

    config_defaults: list[Path] = []
    source_defaults_dir = plugin_dir / "config" / "defaults"
    if not source_defaults_dir.exists():
        source_defaults_dir = DEFAULT_CONFIG_ROOT / plugin_name
    if source_defaults_dir.exists():
        config_defaults_dir.mkdir(parents=True, exist_ok=True)
        for file in sorted(source_defaults_dir.glob("*.json")):
            shutil.copy2(file, config_defaults_dir / file.name)
            config_defaults.append(file)

    packaged_manifest = _build_packaged_manifest(
        data,
        plugin_name,
        widget_files,
        editor_files,
        config_defaults,
    )
    (internal_dir / "plugin.toml").write_text(packaged_manifest, encoding="utf-8")

    _write_manifest_lock(
        package_dir / "manifest.lock",
        plugin_name=plugin_name,
        version=_require_string(data, "version"),
        runtime_artifact=f"runtime/{runtime_artifact.name}",
        runtime_hash=_sha256(runtime_artifact),
        user_files=[
            *[src for src, _ in widget_files],
            *[src for src, _ in editor_files],
            *[f"config/defaults/{file.name}" for file in config_defaults],
        ],
    )

    if create_zip:
        zip_path = output_dir / f"{plugin_name}-{data['version']}.zip"
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
