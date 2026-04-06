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

"""Projection helpers for runtime-owned widget records."""

from __future__ import annotations

from app_schema.plugin import PluginManifest
from runtime.connectors import ConnectorServiceRegistry, required_connector_ids
from runtime.widgets.contracts import WidgetRuntimeRecord, WidgetRuntimeStatus
from runtime.widgets.game_detection import detect_active_game_id


def project_overlay_widget_records(
    plugins: dict[str, PluginManifest],
    connector_services: ConnectorServiceRegistry,
    *,
    plugin_id: str,
    active_plugin: str | None,
) -> list[WidgetRuntimeRecord]:
    """Project overlay widget declarations into runtime-owned records."""

    manifest = plugins.get(plugin_id)
    if manifest is None or manifest.overlay is None:
        return []

    connector_ids = tuple(sorted(required_connector_ids(plugins, plugin_id)))
    available_sources = _available_sources(connector_services, connector_ids)
    records: list[WidgetRuntimeRecord] = []
    for widget in manifest.overlay.widgets:
        source = widget.bindings.get("source", "")
        status = _widget_status(
            plugins=plugins,
            active_plugin=active_plugin,
            overlay_id=plugin_id,
            connector_ids=connector_ids,
            connector_services=connector_services,
            source=source,
            available_sources=available_sources,
        )
        records.append(
            WidgetRuntimeRecord(
                overlay_id=plugin_id,
                widget_id=widget.id,
                widget_type=widget.widget,
                label=widget.label or widget.id,
                source=source,
                status=status,
                connector_ids=connector_ids,
                error_message=f"Source '{source}' is unavailable" if status == WidgetRuntimeStatus.ERROR else "",
            )
        )
    return records


def _available_sources(
    connector_services: ConnectorServiceRegistry,
    connector_ids: tuple[str, ...],
) -> set[str]:
    available: set[str] = set()
    for connector_id in connector_ids:
        if not connector_services.has(connector_id):
            continue
        for key, _ in connector_services.inspect(connector_id):
            available.add(key)
    return available


def _widget_status(
    *,
    plugins: dict[str, PluginManifest],
    active_plugin: str | None,
    overlay_id: str,
    connector_ids: tuple[str, ...],
    connector_services: ConnectorServiceRegistry,
    source: str,
    available_sources: set[str],
) -> WidgetRuntimeStatus:
    if active_plugin != overlay_id:
        return WidgetRuntimeStatus.IDLE
    if any(not connector_services.has(connector_id) for connector_id in connector_ids):
        return WidgetRuntimeStatus.WAITING_FOR_CONNECTOR
    if _waiting_for_game(plugins, connector_services, connector_ids):
        return WidgetRuntimeStatus.WAITING_FOR_GAME
    if source and source not in available_sources:
        return WidgetRuntimeStatus.ERROR
    return WidgetRuntimeStatus.READY


def _waiting_for_game(
    plugins: dict[str, PluginManifest],
    connector_services: ConnectorServiceRegistry,
    connector_ids: tuple[str, ...],
) -> bool:
    for connector_id in connector_ids:
        manifest = plugins.get(connector_id)
        connector = manifest.connector if manifest is not None else None
        if connector is None or not connector.games:
            continue
        if not connector_services.has(connector_id):
            return True
        if detect_active_game_id(connector.games) is None:
            return True
    return False
