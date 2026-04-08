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

"""Internal connector service lifecycle policy for runtime V2."""

from __future__ import annotations

from runtimeV2.connectors.service_loader import load_connector_service
from runtimeV2.connectors.service_registry import ConnectorServiceRegistry
from runtimeV2.plugins.schemas import PluginManifest


def register_connector_service(
    *,
    manifest: PluginManifest,
    connector_services: ConnectorServiceRegistry,
) -> bool:
    """Register a manifest-declared connector service."""

    connector = manifest.connector
    if (
        connector is None
        or connector.service is None
        or connector_services.has(manifest.plugin_id)
    ):
        return False

    service = load_connector_service(connector.service.module, connector.service.class_name)
    connector_services.register(
        manifest.plugin_id,
        manifest.plugin_id,
        manifest.plugin_id,
        service,
    )
    return True


def unregister_connector_service(
    *,
    manifest: PluginManifest,
    connector_services: ConnectorServiceRegistry,
) -> bool:
    """Unregister a manifest-declared connector service."""

    return connector_services.unregister(manifest.plugin_id)
