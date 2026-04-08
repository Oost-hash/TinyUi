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

from runtime_schema import StartupResult, startup_error, startup_ok
from runtimeV2.connectors.capabilities.connector_read import ConnectorRead
from runtimeV2.plugins.capabilities.active_read import PluginActiveRead
from runtimeV2.plugins.capabilities.connector_decl_read import PluginConnectorDeclRead
from runtimeV2.plugins.capabilities.overlay_decl_read import PluginOverlayDeclRead
from runtimeV2.runtime import RuntimeV2
from runtimeV2.widgets.capabilities.widget_records_read import WidgetRecordsRead
from runtimeV2.widgets.contracts import WidgetRecord
from runtimeV2.widgets.projection import project_widget_records
from runtimeV2.widgets.register_capabilities import register_widget_capabilities


@dataclass(frozen=True)
class WidgetsStartupResult:
    """Result of widgets domain startup."""

    records: list[WidgetRecord]
    records_read: WidgetRecordsRead


def startup_widgets(runtime: RuntimeV2) -> StartupResult:
    """Start the widgets domain."""

    try:
        records = project_widget_records(
            overlay_read=runtime.capability("plugin_overlay_decl_read", PluginOverlayDeclRead),
            connector_decl_read=runtime.capability("plugin_connector_decl_read", PluginConnectorDeclRead),
            connector_read=runtime.capability("connector_read", ConnectorRead),
            active_read=runtime.capability("plugin_active_read", PluginActiveRead),
        )
        records_read = register_widget_capabilities(records)
        runtime.register_capability("widget_records_read", records_read)
        runtime.register_domain_result("widgets", WidgetsStartupResult(
            records=records,
            records_read=records_read,
        ))
        return startup_ok()
    except Exception as exc:
        return startup_error(f"Widgets domain startup failed: {exc}")
