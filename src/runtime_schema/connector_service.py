"""Connector service lifecycle event schemas."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ConnectorServiceRegisteredData:
    """Data for connector service registration events."""

    connector_id: str
    plugin_id: str
    display_name: str = ""
    source: str = "connector"


@dataclass(frozen=True)
class ConnectorServiceUnregisteredData:
    """Data for connector service removal events."""

    connector_id: str
    plugin_id: str


@dataclass(frozen=True)
class ConnectorServiceUpdatedData:
    """Data for connector service snapshot/source updates."""

    connector_id: str
    plugin_id: str
