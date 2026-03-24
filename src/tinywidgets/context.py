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
        self._flash_target = "value"

    def update(self, state: WidgetState) -> None:
        self._text         = state.text
        self._color        = state.color
        self._visible      = state.visible
        self._text_visible = state.text_visible
        self._flash_target = state.flash_target
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

    @Slot(int, str)
    def setThresholdColor(self, index: int, color: str) -> None:
        if 0 <= index < len(self._spec.thresholds):
            e = self._spec.thresholds[index]
            self._spec.thresholds[index] = ThresholdEntry(e.value, color, e.flash, e.flash_speed, e.flash_target)
            self.configChanged.emit()

    @Slot(int, float)
    def setThresholdValue(self, index: int, value: float) -> None:
        if 0 <= index < len(self._spec.thresholds):
            e = self._spec.thresholds[index]
            self._spec.thresholds[index] = ThresholdEntry(value, e.color, e.flash, e.flash_speed, e.flash_target)
            self.configChanged.emit()

    @Slot(int, bool)
    def setThresholdFlash(self, index: int, flash: bool) -> None:
        if 0 <= index < len(self._spec.thresholds):
            e = self._spec.thresholds[index]
            self._spec.thresholds[index] = ThresholdEntry(e.value, e.color, flash, e.flash_speed, e.flash_target)
            self.configChanged.emit()

    @Slot(int, int)
    def setThresholdFlashSpeed(self, index: int, ticks: int) -> None:
        if 0 <= index < len(self._spec.thresholds):
            e = self._spec.thresholds[index]
            self._spec.thresholds[index] = ThresholdEntry(e.value, e.color, e.flash, max(1, ticks), e.flash_target)
            self.configChanged.emit()

    @Slot(int, str)
    def setThresholdFlashTarget(self, index: int, target: str) -> None:
        if target in ("value", "text", "widget") and 0 <= index < len(self._spec.thresholds):
            e = self._spec.thresholds[index]
            self._spec.thresholds[index] = ThresholdEntry(e.value, e.color, e.flash, e.flash_speed, target)
            self.configChanged.emit()

    @Slot(float, str)
    def addThreshold(self, value: float, color: str) -> None:
        self._spec.thresholds.append(ThresholdEntry(value, color, False, 5, "value"))
        self.configChanged.emit()

    @Slot()
    def addDefaultThreshold(self) -> None:
        """Append a new threshold whose value is 10 above the current last entry (or 10 if empty)."""
        ts = self._spec.thresholds
        next_val = (ts[-1].value + 10) if ts else 10
        self._spec.thresholds.append(ThresholdEntry(next_val, "#E0E0E0", False, 5, "value"))
        self.configChanged.emit()

    @Slot(int)
    def removeThreshold(self, index: int) -> None:
        if 0 <= index < len(self._spec.thresholds):
            self._spec.thresholds.pop(index)
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

    @Property(str, notify=stateChanged)
    def flashTarget(self) -> str:
        """Current flash target — driven by the active threshold, updates on stateChanged."""
        return self._flash_target

    @Property("QVariantList", notify=configChanged)
    def thresholds(self) -> list:
        """Each entry: {value, color, flash, flashSpeed, flashTarget}."""
        return [{"value":       t.value,
                 "color":       t.color,
                 "flash":       t.flash,
                 "flashSpeed":  t.flash_speed,
                 "flashTarget": t.flash_target}
                for t in self._spec.thresholds]

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

    @property
    def contexts(self) -> list[WidgetContext]:
        """Return all registered widget contexts (Python-side access only)."""
        return list(self._widgets)

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
