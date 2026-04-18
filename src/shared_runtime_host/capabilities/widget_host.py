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

"""Shared host-facing projection for runtime V2 widget records."""

from __future__ import annotations

from numbers import Real
from typing import Any

from runtimeV2.contracts import WidgetRecord, WidgetRecordsReader, WidgetStatus
from runtimeV2.widgets.type_defaults import TEXT_WIDGET_DEFAULTS


class WidgetHostCapability:
    """Project widget runtime records into host-facing shapes."""

    def __init__(self, widget_records_read: WidgetRecordsReader) -> None:
        self._widget_records_read = widget_records_read

    def panel_records(self) -> list[dict[str, object]]:
        """Return widget records for panel/devtools style views."""

        return [self.panel_record(record) for record in self._widget_records_read.all_widget_records()]

    def records(self) -> list[WidgetRecord]:
        """Return the current widget runtime records."""

        return self._widget_records_read.all_widget_records()

    def panel_record(self, record: WidgetRecord) -> dict[str, object]:
        """Return one widget record in panel-oriented shape."""

        return {
            "overlayId": record.overlay_id,
            "widgetId": record.widget_id,
            "widgetType": record.widget_type,
            "label": record.label,
            "source": record.source,
            "bindings": dict(record.bindings),
            "status": record.status.value,
            "connectorIds": list(record.connector_ids),
            "enabled": record.enabled,
            "position": {"x": record.position[0], "y": record.position[1]},
            "values": {} if record.values is None else dict(record.values),
            "resolvedValue": record.resolved_value,
            "errorMessage": record.error_message,
        }

    def window_data(self, record: WidgetRecord) -> dict[str, Any]:
        """Return one widget record in floating-window shape."""

        return {
            "widgetId": record.widget_id,
            "overlayId": record.overlay_id,
            "label": record.label,
            "source": record.source,
            "bindings": dict(record.bindings),
            "values": {} if record.values is None else dict(record.values),
            "resolvedValue": record.resolved_value,
            "displayText": self.display_text(record),
            "textColor": _string_value(record.values, "textColor", "#FF7A7A" if record.status == WidgetStatus.ERROR else _text_default_string("textColor", "#E8EDF2")),
            "backgroundColor": _string_value(record.values, "backgroundColor", _text_default_string("backgroundColor", "#20242b")),
            "width": _int_value(record.values, "width", _text_default_int("width", 220)),
            "height": _int_value(record.values, "height", _text_default_int("height", 72)),
            "fontSize": _int_value(record.values, "fontSize", _text_default_int("fontSize", 18)),
            "visible": record.status != WidgetStatus.HIDDEN,
            "enabled": record.enabled,
            "status": record.status.value,
            "x": record.position[0],
            "y": record.position[1],
        }

    def display_text(self, record: WidgetRecord) -> str:
        """Return widget display text for host surfaces."""

        if record.status == WidgetStatus.READY:
            return _format_display_value(record.resolved_value or record.source, record.values)
        if record.status == WidgetStatus.WAITING_FOR_CONNECTOR:
            return "Waiting for connector"
        if record.status == WidgetStatus.ERROR:
            return record.error_message or "Widget error"
        if record.status == WidgetStatus.HIDDEN:
            return "Hidden"
        return ""


def _format_display_value(value: str, values: dict[str, object] | None) -> str:
    if not value or values is None:
        return value
    raw_format = values.get("format")
    if not isinstance(raw_format, str) or not raw_format:
        return value
    for candidate in (value, _numeric_value(value)):
        if candidate is None:
            continue
        try:
            return raw_format.format(candidate)
        except (IndexError, KeyError, TypeError, ValueError):
            continue
    return value


def _string_value(values: dict[str, object] | None, key: str, fallback: str) -> str:
    if values is None:
        return fallback
    value = values.get(key)
    return str(value) if value is not None else fallback


def _text_default_string(key: str, fallback: str) -> str:
    value = TEXT_WIDGET_DEFAULTS.get(key)
    return value if isinstance(value, str) else fallback


def _text_default_int(key: str, fallback: int) -> int:
    value = TEXT_WIDGET_DEFAULTS.get(key)
    return value if isinstance(value, int) else fallback


def _int_value(values: dict[str, object] | None, key: str, fallback: int) -> int:
    if values is None:
        return fallback
    value = values.get(key)
    if isinstance(value, bool):
        return fallback
    if isinstance(value, int | float):
        return int(value)
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return fallback
    return fallback


def _bool_value(values: dict[str, object] | None, key: str, fallback: bool) -> bool:
    if values is None:
        return fallback
    value = values.get(key)
    return value if isinstance(value, bool) else fallback


def _numeric_value(value: object) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, Real):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return None
    return None
