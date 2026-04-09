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

"""Read-model registry for runtime V2 plugin discovery."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class PluginRecord:
    """Discovery record for one plugin."""

    plugin_id: str
    plugin_root: Path
    source: str


class PluginRegistry:
    """Discovery/read-model storage for plugin manifests and roots."""

    def __init__(self) -> None:
        self._records: dict[str, PluginRecord] = {}
        self._import_roots: set[Path] = set()
        self._skipped_packaged_plugins: set[str] = set()

    def register_plugin(
        self,
        *,
        plugin_id: str,
        plugin_root: Path,
        source: str,
    ) -> None:
        """Register one discovered plugin."""

        self._records[plugin_id] = PluginRecord(
            plugin_id=plugin_id,
            plugin_root=plugin_root,
            source=source,
        )

    def register_import_root(self, import_root: Path) -> None:
        """Register one import root discovered for plugins."""

        self._import_roots.add(import_root)

    def register_skipped_packaged_plugin(self, plugin_id: str) -> None:
        """Record a packaged plugin skipped by this read-only slice."""

        self._skipped_packaged_plugins.add(plugin_id)

    def plugin_ids(self) -> list[str]:
        """Return discovered plugin ids."""

        return list(self._records)

    def plugin_root(self, plugin_id: str) -> Path | None:
        """Return one plugin root."""

        record = self._records.get(plugin_id)
        return None if record is None else record.plugin_root

    def import_roots(self) -> set[Path]:
        """Return discovered import roots."""

        return set(self._import_roots)

    def skipped_packaged_plugins(self) -> set[str]:
        """Return packaged plugins skipped by this read-only slice."""

        return set(self._skipped_packaged_plugins)
