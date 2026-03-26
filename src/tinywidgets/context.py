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
    from tinycore.session import ProviderControlService


class WidgetContext(QObject):
    """Live state of one widget, exposed as QML properties.

    The runner calls update() whenever state changes.
    QML binds to text, color, visible, label, widgetX, widgetY, thresholds, etc.
    """

    stateChanged    = Signal()
    positionChanged = Signal()
    configChanged   = Signal()
    demoChanged     = Signal()

    def __init__(
        self,
        spec: WidgetSpec,
        controls: "ProviderControlService",
        consumer_name: str,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._spec         = spec
        self._controls     = controls
        self._consumer_name = consumer_name
        self._text         = ""
        self._color        = "#E0E0E0"
        self._enabled      = spec.enable
        self._runtime_visible = True
        self._text_visible = True
        self._flash_target = "value"
        self._demo_requested = False
        self._demo_owner = f"widget-settings:{consumer_name}:{spec.id}"

    def _provider_name(self) -> str:
        return self._controls.provider_name_for(self._consumer_name, self._spec.capability)

    def update(self, state: WidgetState) -> None:
        self._text         = state.text
        self._color        = state.color
        self._runtime_visible = state.visible
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

    @Slot(bool)
    def setEnabled(self, enabled: bool) -> None:
        if self._spec.enable == enabled:
            return
        self._spec.enable = enabled
        self._enabled = enabled
        self.configChanged.emit()
        self.stateChanged.emit()

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

    @Slot()
    def requestDemo(self) -> None:
        if not self._provider_name() or not self.supportsDemoMode or self._demo_requested:
            return
        if not self._controls.request_demo_mode(self._consumer_name, self._spec.capability, self._demo_owner):
            return
        self._demo_requested = True
        self.demoChanged.emit()

    @Slot()
    def releaseDemo(self) -> None:
        if not self._provider_name() or not self._demo_requested:
            return
        if not self._controls.release_demo_mode(self._consumer_name, self._spec.capability, self._demo_owner):
            return
        self._demo_requested = False
        self.demoChanged.emit()

    @Slot(float)
    def setDemoMin(self, value: float) -> None:
        if not self._controls.set_demo_min(self._consumer_name, self._spec.capability, value):
            return
        self.demoChanged.emit()

    @Slot(float)
    def setDemoMax(self, value: float) -> None:
        if not self._controls.set_demo_max(self._consumer_name, self._spec.capability, value):
            return
        self.demoChanged.emit()

    @Slot(float)
    def setDemoSpeed(self, value: float) -> None:
        if not self._controls.set_demo_speed(self._consumer_name, self._spec.capability, value):
            return
        self.demoChanged.emit()

    # ── Live state properties ─────────────────────────────────────────────────

    @Property(str, notify=stateChanged)
    def text(self) -> str:
        return self._text

    @Property(str, notify=stateChanged)
    def color(self) -> str:
        return self._color

    @Property(bool, notify=stateChanged)
    def visible(self) -> bool:
        return self._enabled and self._runtime_visible

    @Property(bool, notify=configChanged)
    def enabled(self) -> bool:
        return self._enabled

    @Property(bool, notify=stateChanged)
    def runtimeVisible(self) -> bool:
        return self._runtime_visible

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
    def capability(self) -> str:
        return self._spec.capability

    @Property(str, constant=True)
    def field(self) -> str:
        return self._spec.field

    @Property(str, constant=True)
    def formatStr(self) -> str:
        return self._spec.format

    @Property(str, notify=demoChanged)
    def providerName(self) -> str:
        return self._provider_name()

    @Property(bool, notify=demoChanged)
    def supportsDemoMode(self) -> bool:
        return self._controls.supports_demo_mode(self._consumer_name, self._spec.capability)

    @Property(bool, notify=demoChanged)
    def demoRequested(self) -> bool:
        return self._demo_requested

    @Property(str, notify=demoChanged)
    def providerMode(self) -> str:
        return self._controls.provider_mode(self._consumer_name, self._spec.capability)

    @Property(str, notify=demoChanged)
    def activeGame(self) -> str:
        return self._controls.active_game(self._consumer_name, self._spec.capability)

    @Property(float, notify=demoChanged)
    def demoMin(self) -> float:
        return self._demo_config().minimum

    @Property(float, notify=demoChanged)
    def demoMax(self) -> float:
        return self._demo_config().maximum

    @Property(float, notify=demoChanged)
    def demoSpeed(self) -> float:
        return self._demo_config().speed

    def _demo_config(self):
        return self._controls.demo_config(self._consumer_name, self._spec.capability)

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


class WidgetOverlayState(QObject):
    """Shared overlay visibility state exposed to both QML engines."""

    overlayVisibleChanged = Signal()
    previewWidgetChanged = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._overlay_visible = True
        self._preview_widget_id = ""

    @Property(bool, notify=overlayVisibleChanged)
    def overlayVisible(self) -> bool:
        return self._overlay_visible

    @Property(str, notify=previewWidgetChanged)
    def previewWidgetId(self) -> str:
        return self._preview_widget_id

    @Slot(bool)
    def setOverlayVisible(self, visible: bool) -> None:
        if self._overlay_visible == visible:
            return
        self._overlay_visible = visible
        self.overlayVisibleChanged.emit()

    @Slot()
    def toggleOverlayVisible(self) -> None:
        self.setOverlayVisible(not self._overlay_visible)

    @Slot(str)
    def setPreviewWidget(self, widget_id: str) -> None:
        if self._preview_widget_id == widget_id:
            return
        self._preview_widget_id = widget_id
        self.previewWidgetChanged.emit()


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
