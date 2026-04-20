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

"""Manifest read capability for runtime V2."""

from pathlib import Path

from runtimeV2.manifest.registry import ManifestRegistry
from runtimeV2.plugins.schemas.manifest import PluginManifest


class ManifestRead:
    """Read loaded plugin manifests."""

    def __init__(self, registry: ManifestRegistry) -> None:
        self._registry = registry

    def plugin_manifest(self, plugin_id: str) -> PluginManifest | None:
        """Return one loaded manifest."""

        return self._registry.manifest(plugin_id)

    def all_manifests(self) -> dict[str, PluginManifest]:
        """Return all loaded manifests."""

        return self._registry.all_manifests()

    def plugin_roles(self) -> dict[str, str]:
        """Return plugin roles by plugin id."""

        return {
            plugin_id: manifest.plugin_type
            for plugin_id, manifest in self._registry.all_manifests().items()
        }

    def resource_root(self, plugin_id: str) -> Path:
        """Return one manifest resource root."""

        return self._registry.resource_root(plugin_id)
