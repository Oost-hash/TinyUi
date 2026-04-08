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

"""Widget record projection for runtime V2."""

from __future__ import annotations

from runtimeV2.connectors.capabilities.connector_read import ConnectorRead
from runtimeV2.plugins.capabilities.active_read import PluginActiveRead
from runtimeV2.plugins.capabilities.connector_decl_read import PluginConnectorDeclRead
from runtimeV2.plugins.capabilities.overlay_decl_read import PluginOverlayDeclRead
from runtimeV2.widgets.contracts import WidgetRecord, WidgetStatus


def project_widget_records(
    *,
    overlay_read: PluginOverlayDeclRead,
    connector_decl_read: PluginConnectorDeclRead,
    connector_read: ConnectorRead,
    active_read: PluginActiveRead,
) -> list[WidgetRecord]:
    """Project overlay declarations into runtime V2 widget records."""

    active_plugin = active_read.get_active_plugin()
    connector_decls = connector_decl_read.connector_declarations()
    records: list[WidgetRecord] = []
    for overlay_id, overlay in overlay_read.overlay_declarations().items():
        connector_ids = tuple(connector_id for connector_id in overlay.connectors if connector_id in connector_decls)
        for widget in overlay.widgets:
            source = widget.bindings.get("source", "")
            status = _widget_status(
                active_plugin=active_plugin,
                overlay_id=overlay_id,
                connector_ids=connector_ids,
                connector_read=connector_read,
            )
            records.append(WidgetRecord(
                overlay_id=overlay_id,
                widget_id=widget.id,
                widget_type=widget.widget,
                label=widget.label or widget.id,
                source=source,
                status=status,
                connector_ids=connector_ids,
            ))
    return records


def _widget_status(
    *,
    active_plugin: str | None,
    overlay_id: str,
    connector_ids: tuple[str, ...],
    connector_read: ConnectorRead,
) -> WidgetStatus:
    if active_plugin != overlay_id:
        return WidgetStatus.IDLE
    if any(not connector_read.has(connector_id) for connector_id in connector_ids):
        return WidgetStatus.WAITING_FOR_CONNECTOR
    return WidgetStatus.READY
