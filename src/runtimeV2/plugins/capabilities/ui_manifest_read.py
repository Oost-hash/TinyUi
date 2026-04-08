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

"""UI manifest read capability for runtime V2 plugins."""

from __future__ import annotations

from runtimeV2.plugins.registry import PluginRegistry
from runtimeV2.plugins.schemas import AppManifest, MenuItem, MenuSeparator, StatusbarItemDecl, TabDecl


class PluginUiManifestRead:
    """Read UI declarations from plugin manifests."""

    def __init__(self, registry: PluginRegistry) -> None:
        self._registry = registry

    def windows(self) -> dict[str, list[AppManifest]]:
        """Return manifest windows by plugin id."""

        return {
            plugin_id: [] if manifest.ui is None else list(manifest.ui.windows)
            for plugin_id, manifest in self._registry.all_manifests().items()
        }

    def tabs(self) -> dict[str, list[TabDecl]]:
        """Return manifest tabs by plugin id."""

        return {
            plugin_id: [] if manifest.ui is None else list(manifest.ui.tabs)
            for plugin_id, manifest in self._registry.all_manifests().items()
        }

    def menus(self) -> dict[str, list[MenuItem | MenuSeparator]]:
        """Return plugin menu declarations by plugin id."""

        return {
            plugin_id: [] if manifest.ui is None else list(manifest.ui.plugin_menu)
            for plugin_id, manifest in self._registry.all_manifests().items()
        }

    def statusbar_items(self) -> dict[str, list[StatusbarItemDecl]]:
        """Return statusbar item declarations by window id."""

        items: dict[str, list[StatusbarItemDecl]] = {}
        for manifest in self._registry.all_manifests().values():
            if manifest.ui is None:
                continue
            for window in manifest.ui.windows:
                items[window.id] = list(window.statusbar)
        return items
