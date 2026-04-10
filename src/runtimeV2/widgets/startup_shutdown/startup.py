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

"""Startup for runtime V2 widgets."""

from __future__ import annotations

from dataclasses import dataclass

from runtimeV2.schemas.startup import StartupResult, startup_error, startup_ok
from runtimeV2.capabilities.runtime_globals import RuntimeGlobals
from runtimeV2.connectors.capabilities.connector_read import ConnectorRead
from runtimeV2.events.startup_shutdown.startup import EventsStartupResult
from runtimeV2.persistence.capabilities.widget_config_read import WidgetConfigRead
from runtimeV2.persistence.capabilities.widget_config_write import WidgetConfigWrite
from runtimeV2.plugins.capabilities.active_read import PluginActiveRead
from runtimeV2.manifest.capabilities.connector_read import ManifestConnectorRead
from runtimeV2.manifest.capabilities.overlay_read import ManifestOverlayRead
from runtimeV2.runtime import RuntimeV2
from runtimeV2.widgets.contracts import WidgetRecord
from runtimeV2.widgets.poller import WidgetRuntimePoller
from runtimeV2.widgets.startup_shutdown.register_events import register_widget_events
from runtimeV2.widgets.startup_shutdown.register_capabilities import WidgetCapabilities, register_widget_capabilities
from runtimeV2.widgets.startup_shutdown.register_globals import register_widget_globals
from runtimeV2.widgets.store import WidgetRecordsStore


@dataclass(frozen=True)
class WidgetsStartupResult:
    """Result of widgets domain startup."""

    store: WidgetRecordsStore
    records: list[WidgetRecord]
    poller: WidgetRuntimePoller
    capabilities: WidgetCapabilities


def startup_widgets(runtime: RuntimeV2) -> StartupResult:
    """Start the widgets domain."""

    try:
        events = runtime.domain_result("events", EventsStartupResult)
        register_widget_events(events.registry)
        overlay_read = runtime.capability("manifest_overlay_read", ManifestOverlayRead)
        connector_decl_read = runtime.capability("manifest_connector_read", ManifestConnectorRead)
        globals_capability = runtime.capability("globals", RuntimeGlobals)
        connector_read = globals_capability.read_global("connector_runtime", ConnectorRead)
        active_read = runtime.capability("plugin_active_read", PluginActiveRead)
        widget_config_read = runtime.capability("widget_config_read", WidgetConfigRead)
        widget_config_write = runtime.capability("widget_config_write", WidgetConfigWrite)
        store = WidgetRecordsStore()
        poller = WidgetRuntimePoller(
            store=store,
            overlay_read=overlay_read,
            connector_decl_read=connector_decl_read,
            connector_read=connector_read,
            active_read=active_read,
            widget_config_read=widget_config_read,
            events=events.bus,
        )
        records = poller.refresh()
        capabilities = register_widget_capabilities(
            store=store,
            poller=poller,
            widget_config_read=widget_config_read,
            widget_config_write=widget_config_write,
            events=events.bus,
        )
        runtime.register_capability("widget_records_read", capabilities.records_read)
        runtime.register_capability("widget_records_refresh", capabilities.records_refresh)
        runtime.register_capability("widget_visibility_read", capabilities.visibility_read)
        runtime.register_capability("widget_visibility_write", capabilities.visibility_write)
        register_widget_globals(runtime)
        runtime.register_domain_result("widgets", WidgetsStartupResult(
            store=store,
            records=records,
            poller=poller,
            capabilities=capabilities,
        ))
        return startup_ok()
    except Exception as exc:
        return startup_error(f"Widgets domain startup failed: {exc}")

