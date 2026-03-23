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
"""WidgetContext and WidgetModel — Qt bridge between runners and QML.

WidgetContext   — one QObject per widget, exposes live state as QML properties.
WidgetModel     — holds all contexts, exposes them as a QVariantList for Repeater.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import (
    Property, QAbstractListModel, QModelIndex, QObject, Qt, Signal, Slot,
)

from .runner import WidgetState
from .spec import WidgetSpec
from .threshold import ThresholdEntry

if TYPE_CHECKING:
    pass


class WidgetContext(QObject):
    """Live state of one widget, exposed as QML properties.

    The runner calls update() whenever state changes.
    QML binds to text, color, visible, label, widgetX, widgetY, thresholds, etc.
    """

    stateChanged    = Signal()
    positionChanged = Signal()
    configChanged   = Signal()

    def __init__(self, spec: WidgetSpec, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._spec         = spec
        self._text         = ""
        self._color        = "#E0E0E0"
        self._visible      = True
        self._text_visible = True

    def update(self, state: WidgetState) -> None:
        self._text         = state.text
        self._color        = state.color
        self._visible      = state.visible
        self._text_visible = state.text_visible
        self.stateChanged.emit()

    @Slot(int, int)
    def move(self, x: int, y: int) -> None:
        """Called by QML when the widget is dragged to a new position."""
        self._spec.x = x
        self._spec.y = y
        self.positionChanged.emit()

    # ── Edit slots ────────────────────────────────────────────────────────────

    @Slot(str)
    def setLabel(self, label: str) -> None:
        self._spec.label = label
        self.configChanged.emit()

    @Slot(float)
    def setFlashBelow(self, value: float) -> None:
        self._spec.flash_below = value if value >= 0 else None
        self.configChanged.emit()

    @Slot(int, str)
    def setThresholdColor(self, index: int, color: str) -> None:
        if 0 <= index < len(self._spec.thresholds):
            entry = self._spec.thresholds[index]
            self._spec.thresholds[index] = ThresholdEntry(entry.value, color)
            self.configChanged.emit()

    @Slot(int, float)
    def setThresholdValue(self, index: int, value: float) -> None:
        if 0 <= index < len(self._spec.thresholds):
            entry = self._spec.thresholds[index]
            self._spec.thresholds[index] = ThresholdEntry(value, entry.color)
            self.configChanged.emit()

    # ── Live state properties ─────────────────────────────────────────────────

    @Property(str, notify=stateChanged)
    def text(self) -> str:
        return self._text

    @Property(str, notify=stateChanged)
    def color(self) -> str:
        return self._color

    @Property(bool, notify=stateChanged)
    def visible(self) -> bool:
        return self._visible

    @Property(bool, notify=stateChanged)
    def textVisible(self) -> bool:
        return self._text_visible

    # ── Identity properties (constant) ────────────────────────────────────────

    @Property(str, constant=True)
    def widgetId(self) -> str:
        return self._spec.id

    @Property(str, constant=True)
    def title(self) -> str:
        return self._spec.title

    @Property(str, constant=True)
    def description(self) -> str:
        return self._spec.description

    @Property(str, constant=True)
    def source(self) -> str:
        return self._spec.source

    @Property(str, constant=True)
    def formatStr(self) -> str:
        return self._spec.format

    # ── User-editable config properties ──────────────────────────────────────

    @Property(str, notify=configChanged)
    def label(self) -> str:
        return self._spec.label

    @Property(float, notify=configChanged)
    def flashBelow(self) -> float:
        """Returns -1 when flash is disabled."""
        return self._spec.flash_below if self._spec.flash_below is not None else -1.0

    @Property("QVariantList", notify=configChanged)
    def thresholds(self) -> list:
        """Each entry: {"value": float, "color": str}."""
        return [{"value": t.value, "color": t.color} for t in self._spec.thresholds]

    # ── Position properties ───────────────────────────────────────────────────

    @Property(int, notify=positionChanged)
    def widgetX(self) -> int:
        return self._spec.x

    @Property(int, notify=positionChanged)
    def widgetY(self) -> int:
        return self._spec.y


# ---------------------------------------------------------------------------


class WidgetModel(QAbstractListModel):
    """Holds all WidgetContexts as a proper ListModel for QML Repeater.

    Exposes each item under the role "widgetContext".

    QML usage:
        Repeater {
            model: widgetModel
            delegate: TextWidget { widgetContext: model.widgetContext }
        }
    """

    ContextRole = Qt.UserRole + 1

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._widgets: list[WidgetContext] = []

    def add(self, ctx: WidgetContext) -> None:
        self.beginInsertRows(QModelIndex(), len(self._widgets), len(self._widgets))
        self._widgets.append(ctx)
        self.endInsertRows()

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._widgets)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid() or index.row() >= len(self._widgets):
            return None
        if role == self.ContextRole:
            return self._widgets[index.row()]
        return None

    def roleNames(self) -> dict:
        return {self.ContextRole: b"widgetContext"}
