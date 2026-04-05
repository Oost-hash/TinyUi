"""Connector-specific runtime policy."""

from __future__ import annotations

from app_schema.plugin import PluginManifest
from runtime.connectors.service_loader import load_connector_service
from runtime.connectors.service_registry import ConnectorServiceRegistry
from runtime_schema import (
    ConnectorServiceRegisteredData,
    ConnectorServiceUnregisteredData,
    ConnectorServiceUpdatedData,
    EventType,
)


def required_connector_ids(plugins: dict[str, PluginManifest], plugin_id: str | None) -> set[str]:
    """Return connector ids required by the given UI plugin."""
    if not plugin_id:
        return set()
    manifest = plugins.get(plugin_id)
    if manifest is None:
        return set()
    return {
        required_id
        for required_id in manifest.requires
        if required_id in plugins and plugins[required_id].plugin_type == "connector"
    }


def register_connector_service(
    *,
    plugins: dict[str, PluginManifest],
    connector_services: ConnectorServiceRegistry,
    events,
    plugin_id: str,
) -> None:
    """Instantiate and register a connector-backed service when needed."""
    manifest = plugins[plugin_id]
    connector = manifest.connector
    if (
        connector is None
        or connector.service is None
        or connector_services.has(plugin_id)
    ):
        return

    service = load_connector_service(connector.service.module, connector.service.class_name)
    if hasattr(service, "supports_source") and service.supports_source("mock") and hasattr(service, "request_source"):
        service.request_source("__runtime__", "mock")
    if hasattr(service, "open"):
        service.open()
    connector_services.register(plugin_id, plugin_id, manifest.plugin_id, service)
    events.emit_typed(
        EventType.CONNECTOR_SERVICE_REGISTERED,
        ConnectorServiceRegisteredData(
            connector_id=plugin_id,
            plugin_id=plugin_id,
            display_name=manifest.plugin_id,
        ),
    )
    events.emit_typed(
        EventType.CONNECTOR_SERVICE_UPDATED,
        ConnectorServiceUpdatedData(connector_id=plugin_id, plugin_id=plugin_id),
    )


def unregister_connector_service(
    *,
    connector_services: ConnectorServiceRegistry,
    events,
    plugin_id: str,
) -> None:
    """Close and unregister a connector-backed service when present."""
    service = connector_services.get(plugin_id)
    if service is not None and hasattr(service, "release_source"):
        service.release_source("__runtime__")
    if service is not None and hasattr(service, "close"):
        service.close()
    if connector_services.unregister(plugin_id):
        events.emit_typed(
            EventType.CONNECTOR_SERVICE_UNREGISTERED,
            ConnectorServiceUnregisteredData(connector_id=plugin_id, plugin_id=plugin_id),
        )
