"""Shared host-facing projection for runtime V2 widget records."""

from __future__ import annotations

from typing import Any

from runtimeV2.widgets.capabilities.widget_records_read import WidgetRecordsRead
from runtimeV2.widgets.contracts import WidgetRecord, WidgetStatus


class WidgetHostCapability:
    """Project widget runtime records into host-facing shapes."""

    def __init__(self, widget_records_read: WidgetRecordsRead) -> None:
        self._widget_records_read = widget_records_read

    def panel_records(self) -> list[dict[str, object]]:
        """Return widget records for panel/devtools style views."""

        return [self.panel_record(record) for record in self._widget_records_read.all_widget_records()]

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
            "textColor": "#E0E0E0" if record.status != WidgetStatus.ERROR else "#FF7A7A",
            "backgroundColor": "#CC000000",
            "visible": record.status != WidgetStatus.HIDDEN,
            "enabled": record.enabled,
            "status": record.status.value,
            "x": record.position[0],
            "y": record.position[1],
        }

    def display_text(self, record: WidgetRecord) -> str:
        """Return widget display text for host surfaces."""

        if record.status == WidgetStatus.READY:
            return record.resolved_value or record.source
        if record.status == WidgetStatus.WAITING_FOR_CONNECTOR:
            return "Waiting for connector"
        if record.status == WidgetStatus.ERROR:
            return record.error_message or "Widget error"
        if record.status == WidgetStatus.HIDDEN:
            return "Hidden"
        return ""
