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

"""Plugin icon read capability for runtime V2 plugins."""

from __future__ import annotations

from runtimeV2.manifest.capabilities.manifest_read import ManifestRead
from runtimeV2.plugins.registry import PluginRegistry


class PluginIconCapability:
    """Resolve plugin icon file URLs."""

    def __init__(self, registry: PluginRegistry, manifest_read: ManifestRead) -> None:
        self._registry = registry
        self._manifest_read = manifest_read

    def get_icon_url(self, plugin_id: str) -> str:
        """Return a safe file URL for one plugin icon."""

        manifest = self._manifest_read.plugin_manifest(plugin_id)
        if manifest is None or not manifest.icon:
            return ""

        plugin_root = self._registry.plugin_root(plugin_id)
        if plugin_root is None:
            return ""

        try:
            icon_path = (plugin_root / manifest.icon).resolve()
            icon_path.relative_to(plugin_root.resolve())
        except (OSError, ValueError):
            return ""

        if not icon_path.exists():
            return ""
        return icon_path.as_uri()
