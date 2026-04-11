#  TinyUI
#  Copyright (C) 2026 Oost-hash
#
#  This file is part of TinyUI.
#
#  TinyUI is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  TinyUI is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#  TinyUI builds on TinyPedal by s-victor (https://github.com/s-victor/TinyPedal),
#  licensed under GPLv3.

"""Read-only plugin discovery for runtime V2."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

from pkg_runtime_host import is_packaged_plugin_dir, mount_packaged_plugin
from runtimeV2.contracts import ManifestLoader
from runtimeV2.paths.contracts import RuntimePaths
from runtimeV2.plugins.registry import PluginRegistry


def discover_plugins(runtime_paths: RuntimePaths, manifest_load: ManifestLoader) -> PluginRegistry:
    """Discover host and source plugins into a registry."""

    registry = PluginRegistry()
    _load_host_plugin(registry, runtime_paths, manifest_load)
    _load_external_plugins(registry, runtime_paths, manifest_load)
    _ensure_import_roots(registry)
    return registry


def _load_host_plugin(registry: PluginRegistry, runtime_paths: RuntimePaths, manifest_load: ManifestLoader) -> None:
    manifest_path = runtime_paths.host_dir / "manifest.toml"
    if not manifest_path.exists():
        raise RuntimeError(f"Host plugin manifest not found: {manifest_path}")

    manifest = manifest_load.load_manifest(manifest_path, resource_root=runtime_paths.host_dir, source="host")
    registry.register_plugin(
        plugin_id=manifest.plugin_id,
        plugin_root=runtime_paths.host_dir,
        source="host",
    )
    registry.register_import_root(runtime_paths.host_dir.parent.parent)


def _load_external_plugins(registry: PluginRegistry, runtime_paths: RuntimePaths, manifest_load: ManifestLoader) -> None:
    if not runtime_paths.plugins_dir.exists():
        return

    for plugin_dir in sorted(runtime_paths.plugins_dir.iterdir()):
        if not plugin_dir.is_dir() or plugin_dir.name.startswith("__"):
            continue
        if plugin_dir.name == "tinyui":
            continue
        _load_external_plugin(registry, plugin_dir, manifest_load)


def _load_external_plugin(registry: PluginRegistry, plugin_dir: Path, manifest_load: ManifestLoader) -> None:
    raw_manifest = plugin_dir / "manifest.toml"
    if raw_manifest.exists():
        manifest = manifest_load.load_manifest(raw_manifest, resource_root=plugin_dir, source="source")
        registry.register_plugin(
            plugin_id=manifest.plugin_id,
            plugin_root=plugin_dir,
            source="source",
        )
        registry.register_import_root(plugin_dir.parent.parent)
        return

    if is_packaged_plugin_dir(plugin_dir):
        mounted = mount_packaged_plugin(plugin_dir)
        manifest = manifest_load.load_manifest(
            mounted.manifest_path,
            resource_root=mounted.plugin_root,
            source="packaged",
        )
        registry.register_plugin(
            plugin_id=manifest.plugin_id,
            plugin_root=mounted.plugin_root,
            source="packaged",
        )
        registry.register_import_root(mounted.import_root)


def _ensure_import_roots(registry: PluginRegistry) -> None:
    for import_root in reversed(sorted(registry.import_roots())):
        import_root_text = str(import_root)
        if import_root_text not in sys.path:
            sys.path.insert(0, import_root_text)
        _extend_plugins_package_path(import_root / "plugins")


def _extend_plugins_package_path(package_root: Path) -> None:
    """Expose discovered plugin package roots to an already-imported plugins package."""

    if not package_root.exists():
        return

    plugins_package = sys.modules.get("plugins")
    if plugins_package is None:
        try:
            plugins_package = importlib.import_module("plugins")
        except ModuleNotFoundError:
            return

    package_path = getattr(plugins_package, "__path__", None)
    if package_path is None:
        return

    package_root_text = str(package_root)
    if package_root_text not in package_path:
        package_path.append(package_root_text)
