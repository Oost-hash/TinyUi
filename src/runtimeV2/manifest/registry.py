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

"""Runtime V2 manifest registry."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from runtimeV2.plugins.schemas.manifest import PluginManifest


@dataclass(frozen=True)
class ManifestRecord:
    """One loaded plugin manifest record."""

    plugin_id: str
    manifest: PluginManifest
    manifest_path: Path
    resource_root: Path
    source: str


class ManifestRegistry:
    """Read-model storage for loaded plugin manifests."""

    def __init__(self) -> None:
        self._records: dict[str, ManifestRecord] = {}

    def register_manifest(
        self,
        *,
        manifest: PluginManifest,
        manifest_path: Path,
        resource_root: Path,
        source: str,
    ) -> None:
        """Register one loaded manifest."""

        self._records[manifest.plugin_id] = ManifestRecord(
            plugin_id=manifest.plugin_id,
            manifest=manifest,
            manifest_path=manifest_path,
            resource_root=resource_root,
            source=source,
        )

    def plugin_ids(self) -> list[str]:
        """Return loaded plugin ids."""

        return list(self._records)

    def manifest(self, plugin_id: str) -> PluginManifest | None:
        """Return one loaded manifest."""

        record = self._records.get(plugin_id)
        return None if record is None else record.manifest

    def all_manifests(self) -> dict[str, PluginManifest]:
        """Return all loaded manifests by plugin id."""

        return {plugin_id: record.manifest for plugin_id, record in self._records.items()}

    def resource_root(self, plugin_id: str) -> Path | None:
        """Return one manifest resource root."""

        record = self._records.get(plugin_id)
        return None if record is None else record.resource_root

    def records(self) -> list[ManifestRecord]:
        """Return all manifest records."""

        return list(self._records.values())
