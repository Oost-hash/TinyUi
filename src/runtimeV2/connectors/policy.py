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

from runtimeV2.connectors.contracts import (
    ConnectorServiceRegisteredData,
    ConnectorServiceUnregisteredData,
    ConnectorServiceUpdatedData,
)
from runtimeV2.connectors.schemas.manifest import ConnectorManifest
from runtimeV2.connectors.service_loader import load_connector_service
from runtimeV2.connectors.service_registry import ConnectorServiceRegistry
from runtimeV2.events.contracts import EventBus, EventType


def register_connector_service(
    *,
    connector_id: str,
    declaration: ConnectorManifest,
    connector_services: ConnectorServiceRegistry,
    events: EventBus | None = None,
) -> bool:
    """Instantiate and register a connector-backed service when declared."""

    if declaration.service is None or connector_services.has(connector_id):
        return False

    service = load_connector_service(declaration.service.module, declaration.service.class_name)
    if hasattr(service, "open"):
        service.open()

    connector_services.register(
        connector_id=connector_id,
        plugin_id=connector_id,
        display_name=connector_id,
        instance=service,
    )
    _emit_registered(events, connector_id)
    return True


def register_declared_connector_services(
    *,
    declarations: dict[str, ConnectorManifest],
    connector_services: ConnectorServiceRegistry,
    events: EventBus | None = None,
) -> list[str]:
    """Register all manifest-declared connector services."""

    registered: list[str] = []
    for connector_id, declaration in declarations.items():
        if register_connector_service(
            connector_id=connector_id,
            declaration=declaration,
            connector_services=connector_services,
            events=events,
        ):
            registered.append(connector_id)
    return registered


def unregister_connector_service(
    *,
    connector_id: str,
    connector_services: ConnectorServiceRegistry,
    events: EventBus | None = None,
) -> bool:
    """Close and unregister a connector-backed service when present."""

    service = connector_services.get(connector_id)
    if service is not None and hasattr(service, "release_source"):
        service.release_source("__runtime__")
    if service is not None and hasattr(service, "close"):
        service.close()
    if not connector_services.unregister(connector_id):
        return False

    if events is not None:
        events.emit_typed(
            EventType.CONNECTOR_SERVICE_UNREGISTERED,
            ConnectorServiceUnregisteredData(
                connector_id=connector_id,
                plugin_id=connector_id,
            ),
            source="connectors",
        )
    return True


def _emit_registered(events: EventBus | None, connector_id: str) -> None:
    """Emit connector registration/update events."""

    if events is None:
        return
    events.emit_typed(
        EventType.CONNECTOR_SERVICE_REGISTERED,
        ConnectorServiceRegisteredData(
            connector_id=connector_id,
            plugin_id=connector_id,
            display_name=connector_id,
        ),
        source="connectors",
    )
    events.emit_typed(
        EventType.CONNECTOR_SERVICE_UPDATED,
        ConnectorServiceUpdatedData(
            connector_id=connector_id,
            plugin_id=connector_id,
        ),
        source="connectors",
    )
