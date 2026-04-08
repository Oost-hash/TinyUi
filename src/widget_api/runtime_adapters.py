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

"""Widget API adapters for runtime V2 handoff objects."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import QObject, Slot

from shared_runtime_host.capabilities.widget_host import WidgetHostCapability
from runtimeV2.persistence.capabilities.widget_config_write import WidgetConfigWrite
from runtimeV2.widgets.contracts import WidgetRecord


class WidgetConfigWriteAdapter(QObject):
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


def widget_data_for_record(widget_host: WidgetHostCapability, record: WidgetRecord) -> dict[str, Any]:
    """Build the widgetData payload expected by widget QML windows."""

    return widget_host.window_data(record)
