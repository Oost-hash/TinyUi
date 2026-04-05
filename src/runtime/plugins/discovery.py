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

"""Plugin discovery — discovers and loads all plugins."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app_schema.plugin import PluginManifest
    from runtime.app.paths import AppPaths


class PluginDiscovery:
    """Discovers and loads plugin manifests from the filesystem.

    This class is responsible for:
    - Loading the host plugin (tinyui)
    - Discovering all external plugins
    - Tracking plugin manifests and their locations
    """

    def __init__(self, paths: AppPaths) -> None:
        self._paths = paths
        self._plugins: dict[str, PluginManifest] = {}
        self._plugin_roots: dict[str, Path] = {}
        self._plugin_import_roots: set[str] = set()

    # ── Discovery ─────────────────────────────────────────────────────────

    def discover_all(self) -> dict[str, PluginManifest]:
        """Discover and load all plugins.

        Returns:
            Dictionary mapping plugin IDs to their manifests.
        """
        from runtime.manifest import load_plugin_manifest
        from runtime.plugins.packaged_plugin import resolve_packaged_plugin

        # Load host plugin first
        self._load_host_plugin()

        # Discover external plugins
        if self._paths.plugins_dir.exists():
            for plugin_dir in sorted(self._paths.plugins_dir.iterdir()):
                if not plugin_dir.is_dir() or plugin_dir.name.startswith("__"):
                    continue
                if plugin_dir.name == "tinyui":
                    continue  # Already loaded as host
                self._load_external_plugin(plugin_dir)

        return dict(self._plugins)

    def _load_host_plugin(self) -> None:
        """Load the host plugin (tinyui)."""
        from runtime.manifest import load_plugin_manifest

        manifest_path = self._paths.host_dir / "manifest.toml"
        if not manifest_path.exists():
            raise RuntimeError(f"Host plugin manifest not found: {manifest_path}")

        manifest = load_plugin_manifest(
            manifest_path,
            resource_root=self._paths.host_dir,
        )
        self._plugins["tinyui"] = manifest
        self._plugin_roots["tinyui"] = self._paths.host_dir
        self._plugin_import_roots.add(str(self._paths.host_dir.parent.parent))

    def _load_external_plugin(self, plugin_dir: Path) -> None:
        """Load a single external plugin."""
        from runtime.manifest import load_plugin_manifest
        from runtime.plugins.packaged_plugin import resolve_packaged_plugin

        plugin_id = plugin_dir.name
        raw_manifest = plugin_dir / "manifest.toml"

        if raw_manifest.exists():
            # Raw plugin source
            manifest = load_plugin_manifest(raw_manifest, resource_root=plugin_dir)
            self._plugins[plugin_id] = manifest
            self._plugin_roots[plugin_id] = plugin_dir
            self._plugin_import_roots.add(str(plugin_dir.parent.parent))
        else:
            # Packaged plugin
            packaged = resolve_packaged_plugin(plugin_dir, self._paths)
            if packaged is not None:
                manifest = load_plugin_manifest(
                    packaged.manifest_path,
                    resource_root=packaged.plugin_root,
                )
                self._plugins[plugin_id] = manifest
                self._plugin_roots[plugin_id] = packaged.plugin_root
                if packaged.import_root is not None:
                    self._plugin_import_roots.add(str(packaged.import_root))

    # ── Accessors ─────────────────────────────────────────────────────────

    def get(self, plugin_id: str) -> PluginManifest | None:
        """Get manifest for a specific plugin.

        Args:
            plugin_id: ID of the plugin.

        Returns:
            Plugin manifest or None if not found.
        """
        return self._plugins.get(plugin_id)

    def get_root(self, plugin_id: str) -> Path | None:
        """Get resource root for a specific plugin.

        Args:
            plugin_id: ID of the plugin.

        Returns:
            Plugin resource root or None if not found.
        """
        return self._plugin_roots.get(plugin_id)

    def list_all(self) -> list[str]:
        """List all discovered plugin IDs."""
        return list(self._plugins.keys())

    @property
    def import_roots(self) -> set[str]:
        """Python import roots for discovered plugins."""
        return set(self._plugin_import_roots)

    # ── Icon Resolution ────────────────────────────────────────────────────

    def icon_url(self, plugin_id: str) -> str:
        """Resolve icon URL for a plugin.

        Args:
            plugin_id: ID of the plugin.

        Returns:
            URL string for the icon, or empty string if none.
        """
        from pathlib import PurePosixPath

        manifest = self._plugins.get(plugin_id)
        if manifest is None or not manifest.icon:
            return ""

        # Security: ensure icon path doesn't escape plugin root
        icon_path = manifest.icon
        if ".." in icon_path or icon_path.startswith("/"):
            return ""

        root = self._plugin_roots.get(plugin_id)
        if root is None:
            return ""

        # Check file exists
        icon_file = root / icon_path
        try:
            # Ensure the resolved path is within plugin root
            resolved = icon_file.resolve()
            root_resolved = root.resolve()
            if not str(resolved).startswith(str(root_resolved)):
                return ""
            if not resolved.exists():
                return ""
        except (OSError, ValueError):
            return ""

        # Return QML-compatible URL
        return f"file:///{PurePosixPath(icon_file)}"
