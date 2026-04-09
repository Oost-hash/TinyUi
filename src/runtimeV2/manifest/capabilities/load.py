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

"""Manifest load capability for runtime V2."""

from __future__ import annotations

from pathlib import Path

from runtimeV2.manifest.parser import load_plugin_manifest
from runtimeV2.manifest.registry import ManifestRegistry
from runtimeV2.plugins.schemas.manifest import PluginManifest


class ManifestLoad:
    """Load and register plugin manifests."""

    def __init__(self, registry: ManifestRegistry) -> None:
        self._registry = registry

    def load_manifest(self, path: Path, *, resource_root: Path, source: str) -> PluginManifest:
        """Load and register one plugin manifest."""

        manifest = load_plugin_manifest(path, resource_root=resource_root)
        self._registry.register_manifest(
            manifest=manifest,
            manifest_path=path,
            resource_root=resource_root,
            source=source,
        )
        return manifest
