"""Widget-facing host capabilities above runtimeV2."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import QObject, Slot

from shared_runtime_host.capabilities.widget_host import WidgetHostCapability
from runtimeV2.persistence.capabilities.widget_config_write import WidgetConfigWrite
from runtimeV2.widgets.contracts import WidgetRecord


class WidgetConfigWriteQmlCapability(QObject):
    """Expose widget config writes in the shape QML expects."""

    def __init__(self, widget_config_write: WidgetConfigWrite, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._widget_config_write = widget_config_write

    @Slot(str, str, int, int, result=bool)
    def setWidgetPosition(self, overlay_id: str, widget_id: str, x: int, y: int) -> bool:
        """Persist widget position from QML."""

        return self._widget_config_write.set_widget_position(overlay_id, widget_id, x, y)

    @Slot(str, str, bool, result=bool)
    def setWidgetEnabled(self, overlay_id: str, widget_id: str, enabled: bool) -> bool:
        """Persist widget enabled state from QML."""

        return self._widget_config_write.set_widget_enabled(overlay_id, widget_id, enabled)

    @Slot(str, str, "QVariantMap", result=bool)
    def setWidgetValues(self, overlay_id: str, widget_id: str, values: dict[str, object]) -> bool:
        """Persist widget config values from QML."""

        return self._widget_config_write.set_widget_values(overlay_id, widget_id, values)

    @Slot(str, str, result=bool)
    def resetWidgetValues(self, overlay_id: str, widget_id: str) -> bool:
        """Reset widget config values from QML."""

        return self._widget_config_write.reset_widget_values(overlay_id, widget_id)


def widget_window_data(widget_host: WidgetHostCapability, record: WidgetRecord) -> dict[str, Any]:
    """Build the widgetData payload expected by widget QML windows."""

    return widget_host.window_data(record)
