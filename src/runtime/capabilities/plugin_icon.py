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

"""Plugin icon capability — manages plugin icon URL resolution and validation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from runtime.runtime import Runtime


class PluginIconCapability:
    """Manages plugin icon URL resolution and validation.

    Handles security validation (icon must be within plugin root)
    and caches valid icons to avoid repeated warnings.
    """

    def __init__(self) -> None:
        self._runtime: Runtime | None = None
        self._invalid_plugin_icons: set[str] = set()

    @property
    def name(self) -> str:
        """Unique capability name."""
        return "plugin_icon"

    def attach(self, runtime: Runtime) -> None:
        """Attach to runtime — called on registration."""
        self._runtime = runtime

    def qml_interface(self) -> None:
        """No QML interface for this capability."""
        return None

    def get_icon_url(self, plugin_id: str) -> str:
        """Get icon URL for a plugin.

        Args:
            plugin_id: The plugin ID.

        Returns:
            File URL string if icon exists and is valid, empty string otherwise.
        """
        if self._runtime is None:
            return ""

        manifest = self._runtime.plugin_manifest(plugin_id)
        if manifest is None or not manifest.icon:
            return ""

        plugin_root = self._plugin_root(plugin_id)
        if plugin_root is None:
            return ""

        icon_path = self._resolve_icon_path(plugin_root, manifest.icon)
        if icon_path is None:
            return ""

        if not self._is_valid_icon(icon_path, plugin_root, plugin_id):
            return ""

        self._invalid_plugin_icons.discard(plugin_id)
        return icon_path.as_uri()

    def _plugin_root(self, plugin_id: str) -> Path | None:
        """Get plugin root directory."""
        if self._runtime is None:
            return None

        if plugin_id == "tinyui":
            if self._runtime.paths is None:
                return None
            return self._runtime.paths.host_dir

        # Get plugin root from discovery capability
        discovery = self._runtime.capability("plugin_discovery")
        return discovery.plugin_root(plugin_id)

    def _resolve_icon_path(self, plugin_root: Path, icon: str) -> Path | None:
        """Resolve icon path from plugin root and manifest icon value."""
        try:
            icon_path = (plugin_root / icon).resolve()
            return icon_path
        except (ValueError, OSError):
            return None

    def _is_valid_icon(self, icon_path: Path, plugin_root: Path, plugin_id: str) -> bool:
        """Validate icon path is within plugin root and exists."""
        try:
            icon_path.relative_to(plugin_root)
        except ValueError:
            self._warn_invalid_icon(plugin_id, f"resolved outside plugin root")
            return False

        if not icon_path.exists():
            self._warn_invalid_icon(plugin_id, f"file not found")
            return False

        return True

    def _warn_invalid_icon(self, plugin_id: str, reason: str) -> None:
        """Warn once about invalid icon."""
        if plugin_id in self._invalid_plugin_icons:
            return
        self._invalid_plugin_icons.add(plugin_id)
        print(f"[runtime] Ignoring invalid plugin icon for '{plugin_id}': {reason}", file=sys.stderr)
