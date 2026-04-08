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

"""Manifest schema registration for connectors."""

from runtimeV2.connectors.schemas.manifest import ConnectorGameDecl, ConnectorManifest, ConnectorServiceDecl
from runtimeV2.manifest.schema_registry import ManifestSchemaRegistry


def register_connector_schemas(registry: ManifestSchemaRegistry) -> None:
    """Register connector-owned manifest schemas."""

    registry.register_schema("connector", owner_domain="connectors", schema_type=ConnectorManifest)
    registry.register_schema("connector.game", owner_domain="connectors", schema_type=ConnectorGameDecl)
    registry.register_schema("connector.service", owner_domain="connectors", schema_type=ConnectorServiceDecl)
