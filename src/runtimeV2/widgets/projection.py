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

from runtimeV2.contracts import (
    ConnectorReader,
    ManifestConnectorReader,
    ManifestOverlayReader,
    PluginActiveReader,
    WidgetConfigReader,
)
from runtimeV2.widgets.contracts import WidgetRecord, WidgetStatus


def project_widget_records(
    *,
    overlay_read: ManifestOverlayReader,
    connector_decl_read: ManifestConnectorReader,
    connector_read: ConnectorReader,
    active_read: PluginActiveReader,
    widget_config_read: WidgetConfigReader,
) -> list[WidgetRecord]:
    """Project overlay declarations into runtime V2 widget records."""

    active_plugin = active_read.get_active_plugin()
    connector_decls = connector_decl_read.connector_declarations()
    global_visible = widget_config_read.global_widgets_visible()
    records: list[WidgetRecord] = []
    for overlay_id, overlay in overlay_read.overlay_declarations().items():
        connector_ids = tuple(connector_id for connector_id in overlay.connectors if connector_id in connector_decls)
        for widget in overlay.widgets:
            source = widget.bindings.get("source", "")
            config = widget_config_read.get_widget(overlay_id, widget.id)
            enabled = widget.defaults.enabled if config is None else config.enabled
            position = widget.defaults.position if config is None else config.position
            values = dict(widget.values)
            if config is not None:
                values.update(config.values)
            status = _widget_status(
                active_plugin=active_plugin,
                overlay_id=overlay_id,
                connector_ids=connector_ids,
                connector_read=connector_read,
                global_visible=global_visible,
                enabled=enabled,
            )
            resolved_value = _resolve_widget_value(
                source=source,
                connector_ids=connector_ids,
                connector_read=connector_read,
            )
            records.append(WidgetRecord(
                overlay_id=overlay_id,
                widget_id=widget.id,
                widget_type=widget.widget,
                label=_widget_label(widget.label, widget.id, values),
                source=source,
                bindings=dict(widget.bindings),
                status=status,
                connector_ids=connector_ids,
                enabled=enabled,
                position=position,
                values=values,
                resolved_value=resolved_value,
            ))
    return records


def _widget_label(default_label: str, widget_id: str, values: dict[str, object]) -> str:
    label = values.get("label", default_label or widget_id)
    return str(label) if label is not None else widget_id


def _resolve_widget_value(
    *,
    source: str,
    connector_ids: tuple[str, ...],
    connector_read: ConnectorReader,
) -> str:
    if not source:
        return ""
    for connector_id in connector_ids:
        value = connector_read.value(connector_id, source)
        if value is not None:
            return value
    return ""


def _widget_status(
    *,
    active_plugin: str | None,
    overlay_id: str,
    connector_ids: tuple[str, ...],
    connector_read: ConnectorReader,
    global_visible: bool,
    enabled: bool,
) -> WidgetStatus:
    if not _overlay_runtime_active(
        active_plugin=active_plugin,
        overlay_id=overlay_id,
        connector_ids=connector_ids,
        connector_read=connector_read,
    ):
        return WidgetStatus.IDLE
    if not global_visible or not enabled:
        return WidgetStatus.HIDDEN
    if any(not connector_read.has(connector_id) for connector_id in connector_ids):
        return WidgetStatus.WAITING_FOR_CONNECTOR
    return WidgetStatus.READY


def _overlay_runtime_active(
    *,
    active_plugin: str | None,
    overlay_id: str,
    connector_ids: tuple[str, ...],
    connector_read: ConnectorReader,
) -> bool:
    if active_plugin == overlay_id:
        return True
    for connector_id in connector_ids:
        if connector_read.show_widgets(connector_id) is True:
            return True
    return False
