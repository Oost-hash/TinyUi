"""Internal smoke validation for the packaged demo plugin flow."""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from build_plugin import build_plugin
from tinyplugins.manifest import scan_plugins
from tinyplugins.runtime_loader import load_runtime_class
from tinyplugins.user_files import sync_user_files


def _purge_plugin_modules(prefix: str) -> None:
    to_remove = [name for name in sys.modules if name == prefix or name.startswith(prefix + ".")]
    for name in to_remove:
        sys.modules.pop(name, None)


def main() -> int:
    plugin_dir = ROOT / "src" / "plugins" / "demo"
    output_dir = ROOT / "dist" / "plugins"
    app_root = output_dir.parent
    package_dir = build_plugin(plugin_dir, output_dir, clean=True, create_zip=False)

    expected_paths = [
        package_dir / "runtime" / "demo.pkg",
        package_dir / "widgets" / "widgets.toml",
        package_dir / "editors" / "editors.toml",
        package_dir / "config" / "defaults" / "settings.json",
        package_dir / "_internal" / "plugin.toml",
        package_dir / "manifest.lock",
    ]
    for path in expected_paths:
        if not path.exists():
            raise FileNotFoundError(f"Smoke failed: missing {path}")

    artifact_path = package_dir / "runtime" / "demo.pkg"
    with zipfile.ZipFile(artifact_path) as zf:
        names = set(zf.namelist())
    required_entries = {
        "plugins/demo/__init__.pyc",
        "plugins/demo/plugin.pyc",
    }
    missing_entries = sorted(required_entries - names)
    if missing_entries:
        raise FileNotFoundError(f"Smoke failed: runtime package missing {missing_entries}")

    manifests = scan_plugins(output_dir)
    manifest = next(item for item in manifests if item.name == "demo")
    if manifest.manifest_path != package_dir / "_internal" / "plugin.toml":
        raise RuntimeError("Smoke failed: packaged demo manifest was not discovered from _internal")
    if manifest.widgets_path() != package_dir / "widgets" / "widgets.toml":
        raise RuntimeError("Smoke failed: widgets path did not resolve from packaged plugin root")
    if manifest.editors_path() != package_dir / "editors" / "editors.toml":
        raise RuntimeError("Smoke failed: editors path did not resolve from packaged plugin root")
    if manifest.runtime is None or Path(manifest.runtime.artifact_path) != artifact_path.resolve():
        raise RuntimeError("Smoke failed: packaged runtime artifact was not resolved correctly")

    config_target = app_root / "config" / "demo" / "settings.json"
    if config_target.exists():
        config_target.unlink()
    sync_user_files(app_root, manifests)
    if not config_target.exists():
        raise FileNotFoundError("Smoke failed: default config was not copied into config/demo")
    original = config_target.read_text(encoding="utf-8")
    config_target.write_text('{"userOverride": true}\n', encoding="utf-8")
    sync_user_files(app_root, manifests)
    if config_target.read_text(encoding="utf-8") != '{"userOverride": true}\n':
        raise RuntimeError("Smoke failed: existing user config was overwritten")
    if original == '{"userOverride": true}\n':
        raise RuntimeError("Smoke failed: preserve test did not change the config fixture")

    _purge_plugin_modules("plugins")
    cls = load_runtime_class(
        manifest.consumer_runtime_spec().module,
        manifest.consumer_runtime_spec().cls,
        manifest.consumer_runtime_spec().artifact_path,
    )
    module = sys.modules[cls.__module__]
    module_file = str(getattr(module, "__file__", ""))
    if "_runtime_cache" not in module_file or "src\\plugins\\demo" in module_file:
        raise RuntimeError(f"Smoke failed: runtime loaded from unexpected location: {module_file}")

    print(f"Packaged demo smoke passed: {package_dir}")
    print(f"Loaded runtime module from: {module_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
