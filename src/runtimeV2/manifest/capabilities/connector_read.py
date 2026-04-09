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

"""Connector manifest read capability for runtime V2."""

from runtimeV2.connectors.schemas.manifest import ConnectorManifest
from runtimeV2.manifest.registry import ManifestRegistry


class ManifestConnectorRead:
    """Read connector declarations from plugin manifests."""

    def __init__(self, registry: ManifestRegistry) -> None:
        self._registry = registry

    def connector_declarations(self) -> dict[str, ConnectorManifest]:
        """Return connector declarations by plugin id."""

        return {
            plugin_id: manifest.connector
            for plugin_id, manifest in self._registry.all_manifests().items()
            if manifest.connector is not None
        }
