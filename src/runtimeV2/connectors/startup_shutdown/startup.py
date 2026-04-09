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

"""Startup for runtime V2 connectors."""

from __future__ import annotations

from dataclasses import dataclass

from runtimeV2.connectors.startup_shutdown.register_capabilities import (
    ConnectorCapabilities,
    register_connector_capabilities,
)
from runtimeV2.connectors.poller import ConnectorServicePoller
from runtimeV2.connectors.policy import register_declared_connector_services
from runtimeV2.connectors.startup_shutdown.register_events import register_connector_events
from runtimeV2.connectors.startup_shutdown.register_globals import register_connector_globals
from runtimeV2.connectors.service_registry import ConnectorServiceRegistry
from runtimeV2.events.startup_shutdown.startup import EventsStartupResult
from runtimeV2.connectors.schemas.manifest import ConnectorManifest
from runtimeV2.manifest.capabilities.connector_read import ManifestConnectorRead
from runtimeV2.persistence.capabilities.settings_read import SettingsRead
from runtimeV2.runtime import RuntimeV2
from runtimeV2.scheduler.capabilities.scheduler_write import SchedulerWrite
from runtimeV2.schemas.startup import StartupResult, startup_error, startup_ok


@dataclass(frozen=True)
class ConnectorsStartupResult:
    """Result of connectors domain startup."""

    registry: ConnectorServiceRegistry
    poller: ConnectorServicePoller
    declarations: dict[str, ConnectorManifest]
    capabilities: ConnectorCapabilities


def startup_connectors(runtime: RuntimeV2) -> StartupResult:
    """Start the connectors domain."""

    try:
        events = runtime.domain_result("events", EventsStartupResult)
        register_connector_events(events.registry)
        declarations = runtime.capability(
            "manifest_connector_read",
            ManifestConnectorRead,
        ).connector_declarations()
        registry = ConnectorServiceRegistry()
        register_declared_connector_services(
            declarations=declarations,
            connector_services=registry,
            events=events.bus,
        )
        poller = ConnectorServicePoller(registry, events.bus)
        capabilities = register_connector_capabilities(registry, poller, events.bus)
        runtime.register_capability("connector_read", capabilities.read)
        runtime.register_capability("connector_write", capabilities.write)
        register_connector_globals(runtime)
        scheduler_write = runtime.capability("scheduler_write", SchedulerWrite)
        settings_read = runtime.capability("settings_read", SettingsRead)
        interval_value = settings_read.get("tinyui", "connector_poll_interval_ms")
        interval_ms = int(interval_value) if isinstance(interval_value, int) else 20
        scheduler_write.register_job(
            job_id="connectors.update_all",
            owner_domain="connectors",
            interval_ms=interval_ms,
            callback=poller.update_all,
        )
        runtime.register_domain_result("connectors", ConnectorsStartupResult(
            registry=registry,
            poller=poller,
            declarations=declarations,
            capabilities=capabilities,
        ))
        return startup_ok()
    except Exception as exc:
        return startup_error(f"Connectors domain startup failed: {exc}")

