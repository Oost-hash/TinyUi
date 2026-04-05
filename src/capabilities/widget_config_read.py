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

"""Widget config read capability."""

from __future__ import annotations

from PySide6.QtCore import Property, QObject, Signal

from runtime.persistence import WidgetConfigStore


class WidgetConfigRead(QObject):
    """Read widget configuration for QML consumers."""

    configsChanged = Signal()

    def __init__(
        self,
        widget_store: WidgetConfigStore,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._widget_store = widget_store
        self._current_overlay: str = ""
        self._configs: list[dict] = []

    def setOverlay(self, overlay_id: str) -> None:
        """Set which overlay's widgets to read."""
        self._current_overlay = overlay_id
        self.refresh()

    def refresh(self) -> None:
        """Refresh widget configs from store."""
        self._configs = self._build_configs()
        self.configsChanged.emit()

    def _build_configs(self) -> list[dict]:
        """Build widget configs for current overlay."""
        if not self._current_overlay:
            return []

        configs = self._widget_store.load_for_overlay(self._current_overlay)
        return [
            {
                "widgetId": c.widget_id,
                "enabled": c.enabled,
                "position": {"x": c.position[0], "y": c.position[1]},
                "values": c.values,
            }
            for c in configs
        ]

    @Property(list, notify=configsChanged)
    def configs(self) -> list[dict]:
        """Widget configurations for current overlay."""
        return list(self._configs)

    def getWidget(self, widget_id: str) -> dict | None:
        """Get configuration for specific widget."""
        for config in self._configs:
            if config["widgetId"] == widget_id:
                return config
        return None
