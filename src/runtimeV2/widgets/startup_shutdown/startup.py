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
from runtimeV2.contracts import (
    ConnectorReader,
    ManifestConnectorReader,
    ManifestOverlayReader,
    PluginActiveReader,
    SchedulerClockReader,
    SchedulerWriter,
    WidgetConfigReader,
    WidgetConfigWriter,
)
from runtimeV2.events.startup_shutdown.startup import EventsStartupResult
from runtimeV2.persistence.startup_shutdown.startup import PersistenceStartupResult
from runtimeV2.runtime import RuntimeV2
from runtimeV2.widgets.contracts import WidgetRecord
from runtimeV2.widgets.startup_shutdown.register_events import register_widget_events
from runtimeV2.widgets.startup_shutdown.register_capabilities import WidgetCapabilities, register_widget_capabilities
from runtimeV2.widgets.startup_shutdown.register_globals import register_widget_globals
from runtimeV2.widgets.startup_shutdown.register_overlay_index import register_overlay_index
from runtimeV2.widgets.startup_shutdown.register_persistence import register_widget_persistence_schemas
from runtimeV2.widgets.store import WidgetRecordsStore


@dataclass(frozen=True)
class WidgetsStartupResult:
    """Result of widgets domain startup."""

    store: WidgetRecordsStore
    records: list[WidgetRecord]
    capabilities: WidgetCapabilities


def startup_widgets(runtime: RuntimeV2) -> StartupResult:
    """Start the widgets domain."""

    try:
        events = runtime.domain_result("events", EventsStartupResult)
        persistence = runtime.domain_result("persistence", PersistenceStartupResult)
        register_widget_events(events.registry)
        register_widget_persistence_schemas(persistence.registry)
        overlay_read = runtime.capability("manifest_overlay_read", ManifestOverlayReader)
        register_overlay_index(
            overlay_read=overlay_read,
            overlay_index=persistence.overlay_index,
        )
        connector_decl_read = runtime.capability("manifest_connector_read", ManifestConnectorReader)
        globals_capability = runtime.capability("globals", RuntimeGlobals)
        connector_read = globals_capability.read_global("connector_runtime", ConnectorReader)
        active_read = runtime.capability("plugin_active_read", PluginActiveReader)
        widget_config_read = runtime.capability("widget_config_read", WidgetConfigReader)
        widget_config_write = runtime.capability("widget_config_write", WidgetConfigWriter)
        scheduler_write = runtime.capability("scheduler_write", SchedulerWriter)
        scheduler_clock_read = runtime.capability("scheduler_clock_read", SchedulerClockReader)
        store = WidgetRecordsStore()
        capabilities = register_widget_capabilities(
            store=store,
            overlay_read=overlay_read,
            connector_decl_read=connector_decl_read,
            connector_read=connector_read,
            active_read=active_read,
            widget_config_read=widget_config_read,
            widget_config_write=widget_config_write,
            scheduler_write=scheduler_write,
            scheduler_clock_read=scheduler_clock_read,
            events=events.bus,
        )
        capabilities.visibility_write.set_global_visible(False)
        records = capabilities.records_refresh.refresh()
        runtime.register_capability("widget_records_read", capabilities.records_read)
        runtime.register_capability("widget_records_refresh", capabilities.records_refresh)
        capabilities.refresh_policy.attach()
        runtime.register_stop_hook("widgets", capabilities.refresh_policy.close)
        runtime.register_capability("widget_visibility_read", capabilities.visibility_read)
        runtime.register_capability("widget_visibility_write", capabilities.visibility_write)
        runtime.register_capability("widget_manual_override", capabilities.manual_override)
        register_widget_globals(runtime)
        runtime.register_domain_result("widgets", WidgetsStartupResult(
            store=store,
            records=records,
            capabilities=capabilities,
        ))
        return startup_ok()
    except Exception as exc:
        return startup_error(f"Widgets domain startup failed: {exc}")

