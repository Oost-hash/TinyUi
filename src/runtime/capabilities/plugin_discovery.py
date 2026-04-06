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

"""Plugin discovery capability — manages plugin loading and discovery."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

from app_schema.plugin import PluginManifest
from runtime.manifest import load_plugin_manifest
from runtime.plugins.packaged_plugin import resolve_packaged_plugin

if TYPE_CHECKING:
    from runtime.runtime import Runtime


class PluginDiscoveryCapability:
    """Manages plugin discovery, loading, and manifest access.

    Replaces the plugin discovery methods that were previously in Runtime.
    """

    def __init__(self) -> None:
        self._runtime: Runtime | None = None
        self._plugins: dict[str, PluginManifest] = {}
        self._plugin_roots: dict[str, Path] = {}
        self._plugin_import_roots: set[str] = set()

    @property
    def name(self) -> str:
        """Unique capability name."""
        return "plugin_discovery"

    def attach(self, runtime: Runtime) -> None:
        """Attach to runtime — called on registration."""
        self._runtime = runtime

    def qml_interface(self) -> None:
        """No QML interface for this capability."""
        return None

    # ── Public API ─────────────────────────────────────────────────────────

    def load_plugin(self, plugin_id: str) -> bool:
        """Load a plugin by ID. Returns True if loaded successfully."""
        if self._runtime is None:
            return False

        paths = self._runtime.paths
        if paths is None:
            return False

        if plugin_id == "tinyui":
            manifest_path = paths.host_dir / "manifest.toml"
            resource_root = paths.host_dir
            self._plugin_import_roots.add(str(paths.host_dir.parent.parent))
        else:
            plugin_dir = paths.plugins_dir / plugin_id
            raw_manifest_path = plugin_dir / "manifest.toml"
            if raw_manifest_path.exists():
                manifest_path = raw_manifest_path
                resource_root = plugin_dir
                self._plugin_import_roots.add(str(plugin_dir.parent.parent))
            else:
                packaged = resolve_packaged_plugin(plugin_dir, paths)
                if packaged is None:
                    return False
                manifest_path = packaged.manifest_path
                resource_root = packaged.plugin_root
                if packaged.import_root is not None:
                    self._plugin_import_roots.add(str(packaged.import_root))

        if not manifest_path.exists():
            return False

        manifest = load_plugin_manifest(manifest_path, resource_root=resource_root)
        self._validate_manifest_extensions(manifest)
        self._plugins[plugin_id] = manifest
        self._plugin_roots[plugin_id] = resource_root
        return True

    def discover_plugins(self) -> list[str]:
        """Discover and load all available plugins. Returns list of loaded plugin IDs."""
        if self._runtime is None:
            return []

        paths = self._runtime.paths
        if paths is None:
            return []

        loaded: list[str] = []
        for folder in sorted(paths.plugins_dir.iterdir()):
            if not folder.is_dir() or folder.name == "tinyui":
                continue
            if (folder / "manifest.toml").exists() or (folder / "_internal" / "manifest.toml").exists():
                if self.load_plugin(folder.name):
                    loaded.append(folder.name)
        return loaded

    def plugin_ids(self) -> list[str]:
        """Get all loaded plugin IDs."""
        return list(self._plugins.keys())

    def plugin_manifest(self, plugin_id: str) -> PluginManifest | None:
        """Get manifest for a loaded plugin."""
        return self._plugins.get(plugin_id)

    def plugin_root(self, plugin_id: str) -> Path | None:
        """Get resource root for a loaded plugin."""
        if self._runtime is None:
            return None
        if plugin_id == "tinyui":
            paths = self._runtime.paths
            return paths.host_dir if paths else None
        return self._plugin_roots.get(plugin_id)

    def ensure_import_roots(self) -> None:
        """Ensure plugin packages are importable before lifecycle activation."""
        if self._runtime is None:
            return
        paths = self._runtime.paths
        if paths is None:
            return

        plugins_parent = str(paths.plugins_dir.parent)
        import_roots = [plugins_parent, *sorted(self._plugin_import_roots)]
        for import_root in reversed(import_roots):
            if import_root not in sys.path:
                sys.path.insert(0, import_root)

    # ── Internal methods ───────────────────────────────────────────────────

    def _validate_manifest_extensions(self, manifest: PluginManifest) -> None:
        """Validate typed manifest extensions that live outside the generic parser core."""
        if manifest.overlay is None:
            return

        if self._runtime is None:
            return

        unknown_widgets = [
            widget.widget
            for widget in manifest.overlay.widgets
            if not self._runtime.widget_registry.has(widget.widget)
        ]
        if unknown_widgets:
            rendered = ", ".join(sorted(set(unknown_widgets)))
            raise ValueError(
                f"Overlay plugin '{manifest.plugin_id}' references unknown widgets: {rendered}"
            )

        for widget in manifest.overlay.widgets:
            definition = self._runtime.widget_registry.get(widget.widget)
            assert definition is not None
            missing_bindings = [
                binding
                for binding in definition.required_bindings
                if binding not in widget.bindings
            ]
            if missing_bindings:
                rendered = ", ".join(missing_bindings)
                raise ValueError(
                    f"Overlay plugin '{manifest.plugin_id}' widget '{widget.id}' is missing bindings: {rendered}"
                )

    def all_plugins(self) -> dict[str, PluginManifest]:
        """Access to internal plugins dict for other capabilities."""
        return self._plugins.copy()

    def set_plugins_for_test(self, plugins: dict[str, PluginManifest]) -> None:
        """Set plugins dict for testing purposes.

        This bypasses normal discovery and should only be used in tests.
        """
        self._plugins = plugins.copy()
