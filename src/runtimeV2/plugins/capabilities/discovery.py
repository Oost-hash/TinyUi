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

"""Discovery read capability for runtime V2 plugins."""

from __future__ import annotations

from pathlib import Path

from runtimeV2.plugins.registry import PluginRegistry


class PluginDiscoveryCapability:
    """Read discovered plugin ids and roots."""

    def __init__(self, registry: PluginRegistry) -> None:
        self._registry = registry

    def plugin_ids(self) -> list[str]:
        """Return discovered plugin ids."""

        return self._registry.plugin_ids()

    def plugin_root(self, plugin_id: str) -> Path | None:
        """Return one plugin root."""

        return self._registry.plugin_root(plugin_id)

    def import_roots(self) -> set[Path]:
        """Return discovered import roots."""

        return self._registry.import_roots()

    def skipped_packaged_plugins(self) -> set[str]:
        """Return packaged plugins skipped by the read-only slice."""

        return self._registry.skipped_packaged_plugins()
