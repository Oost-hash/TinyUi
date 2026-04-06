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

"""Widget visibility capability — manages global widget visibility state."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, Property, Signal, Slot

from runtime_schema import EventType, WidgetRuntimeUpdatedData

if TYPE_CHECKING:
    from runtime.runtime import Runtime


class WidgetVisibilityCapability(QObject):
    """Manages global widget visibility state.

    This capability tracks whether widgets should be visible globally,
    and exposes the state to QML for UI binding.
    """

    globalVisibleChanged = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._runtime: Runtime | None = None
        self._global_visible = True

    @property
    def name(self) -> str:
        """Unique capability name."""
        return "widget_visibility"

    def attach(self, runtime: Runtime) -> None:
        """Attach to runtime — called on registration."""
        self._runtime = runtime

    def qml_interface(self) -> QObject:
        """Return self as QML-exposed interface."""
        return self

    @Property(bool, notify=globalVisibleChanged)
    def globalVisible(self) -> bool:
        """Get global widget visibility state."""
        return self._global_visible

    @Slot(bool)
    def setGlobalVisible(self, visible: bool) -> None:
        """Set global widget visibility state.

        Args:
            visible: True to show widgets, False to hide.
        """
        if self._global_visible != visible:
            self._global_visible = visible
            self.globalVisibleChanged.emit()
            if self._runtime is not None:
                self._runtime.events.emit_typed(
                    EventType.WIDGET_RUNTIME_UPDATED,
                    WidgetRuntimeUpdatedData(reason="visibility_changed")
                )

    @Slot(str, str, result=bool)
    def isWidgetEnabled(self, overlay_id: str, widget_id: str) -> bool:
        """Check if a specific widget is enabled.

        Args:
            overlay_id: ID of the overlay plugin.
            widget_id: ID of the widget instance.

        Returns:
            True if widget is enabled, False otherwise.
        """
        if self._runtime is None:
            return True
        config = self._runtime.widget_store.get_widget(overlay_id, widget_id)
        return config.enabled if config else True
