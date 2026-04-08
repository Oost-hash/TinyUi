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

import sys
from pathlib import Path

from runtimeV2.paths import RuntimePaths
from runtimeV2.plugins.manifest_parser import load_plugin_manifest
from runtimeV2.plugins.registry import PluginRegistry


def discover_plugins(runtime_paths: RuntimePaths) -> PluginRegistry:
    """Discover host and source plugins into a registry."""

    registry = PluginRegistry()
    _load_host_plugin(registry, runtime_paths)
    _load_external_plugins(registry, runtime_paths)
    _ensure_import_roots(registry)
    return registry


def _load_host_plugin(registry: PluginRegistry, runtime_paths: RuntimePaths) -> None:
    manifest_path = runtime_paths.host_dir / "manifest.toml"
    if not manifest_path.exists():
        raise RuntimeError(f"Host plugin manifest not found: {manifest_path}")

    manifest = load_plugin_manifest(manifest_path, resource_root=runtime_paths.host_dir)
    registry.register_plugin(
        plugin_id="tinyui",
        manifest=manifest,
        plugin_root=runtime_paths.host_dir,
        source="host",
    )
    registry.register_import_root(runtime_paths.host_dir.parent.parent)


def _load_external_plugins(registry: PluginRegistry, runtime_paths: RuntimePaths) -> None:
    if not runtime_paths.plugins_dir.exists():
        return

    for plugin_dir in sorted(runtime_paths.plugins_dir.iterdir()):
        if not plugin_dir.is_dir() or plugin_dir.name.startswith("__"):
            continue
        if plugin_dir.name == "tinyui":
            continue
        _load_external_plugin(registry, plugin_dir)


def _load_external_plugin(registry: PluginRegistry, plugin_dir: Path) -> None:
    raw_manifest = plugin_dir / "manifest.toml"
    if raw_manifest.exists():
        manifest = load_plugin_manifest(raw_manifest, resource_root=plugin_dir)
        registry.register_plugin(
            plugin_id=plugin_dir.name,
            manifest=manifest,
            plugin_root=plugin_dir,
            source="source",
        )
        registry.register_import_root(plugin_dir.parent.parent)
        return

    if (plugin_dir / "_internal" / "manifest.toml").exists():
        registry.register_skipped_packaged_plugin(plugin_dir.name)


def _ensure_import_roots(registry: PluginRegistry) -> None:
    for import_root in reversed(sorted(registry.import_roots())):
        import_root_text = str(import_root)
        if import_root_text not in sys.path:
            sys.path.insert(0, import_root_text)
