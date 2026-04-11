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

"""Widget-facing host capabilities above runtimeV2."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import QObject, Signal, Slot

from shared_runtime_host.capabilities.widget_host import WidgetHostCapability
from runtimeV2.contracts import SchedulerWriter, WidgetConfigWriter, WidgetRecord
from widget_api.capabilities import FlashCapability, ThresholdCapability
from widget_api.capabilities.threshold import numeric_value, threshold_entries


class WidgetConfigWriteQmlCapability(QObject):
    """Expose widget config writes in the shape QML expects."""

    def __init__(self, widget_config_write: WidgetConfigWriter, parent: QObject | None = None) -> None:
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


class WidgetEffectsQmlCapability(QObject):
    """Expose widget host effect state to QML."""

    effectsChanged = Signal(str, str)

    def __init__(
        self,
        scheduler_write: SchedulerWriter,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._flash = FlashCapability()
        self._threshold = ThresholdCapability()
        self._colors: dict[str, str] = {}
        self._color_targets: dict[str, str] = {}
        self._keys: dict[str, tuple[str, str]] = {}
        scheduler_write.register_job(
            job_id="widget_api.effects.flash",
            owner_domain="widget_api",
            interval_ms=100,
            callback=self.tick,
            enabled=True,
        )

    def update_widget(self, widget_data: dict[str, object]) -> None:
        """Refresh effect state from one widget data payload."""

        overlay_id = str(widget_data.get("overlayId", ""))
        widget_id = str(widget_data.get("widgetId", ""))
        if not overlay_id or not widget_id:
            return
        widget_key = _widget_key(overlay_id, widget_id)
        self._keys[widget_key] = (overlay_id, widget_id)

        values = widget_data.get("values", {})
        raw_thresholds = values.get("thresholds") if isinstance(values, dict) else []
        thresholds = threshold_entries(raw_thresholds)
        threshold_state = self._threshold.evaluate(
            thresholds,
            numeric_value(widget_data.get("resolvedValue", widget_data.get("displayText", ""))),
        )

        old_color = self._colors.get(widget_key)
        old_color_target = self._color_targets.get(widget_key)
        if threshold_state.color:
            self._colors[widget_key] = threshold_state.color
            self._color_targets[widget_key] = threshold_state.color_target
        else:
            self._colors.pop(widget_key, None)
            self._color_targets.pop(widget_key, None)

        flash_changed = self._flash.set_flash(
            widget_key,
            active=threshold_state.active and threshold_state.flash,
            interval_ticks=threshold_state.flash_speed,
            target=threshold_state.flash_target,
        )
        if (
            flash_changed
            or old_color != self._colors.get(widget_key)
            or old_color_target != self._color_targets.get(widget_key)
        ):
            self.effectsChanged.emit(overlay_id, widget_id)

    @Slot("QVariantMap")
    def updateWidget(self, widget_data: dict[str, object]) -> None:
        """Refresh effect state from QML."""

        self.update_widget(widget_data)

    def remove_widget(self, overlay_id: str, widget_id: str) -> None:
        """Remove effect state for one widget."""

        widget_key = _widget_key(overlay_id, widget_id)
        removed = self._flash.remove(widget_key)
        removed = self._colors.pop(widget_key, None) is not None or removed
        removed = self._color_targets.pop(widget_key, None) is not None or removed
        self._keys.pop(widget_key, None)
        if removed:
            self.effectsChanged.emit(overlay_id, widget_id)

    @Slot(str, str)
    def removeWidget(self, overlay_id: str, widget_id: str) -> None:
        """Remove effect state from QML."""

        self.remove_widget(overlay_id, widget_id)

    @Slot(str, str, result=bool)
    def flashVisible(self, overlay_id: str, widget_id: str) -> bool:
        """Return whether the flashed widget part should be visible."""

        return self._flash.state(_widget_key(overlay_id, widget_id)).visible

    @Slot(str, str, result=str)
    def flashTarget(self, overlay_id: str, widget_id: str) -> str:
        """Return the active flash target."""

        return self._flash.state(_widget_key(overlay_id, widget_id)).target

    @Slot(str, str, str, result=str)
    def textColor(self, overlay_id: str, widget_id: str, fallback: str) -> str:
        """Return threshold color or fallback widget text color."""

        return self._colors.get(_widget_key(overlay_id, widget_id), fallback)

    @Slot(str, str, result=str)
    def colorTarget(self, overlay_id: str, widget_id: str) -> str:
        """Return the active threshold color target."""

        return self._color_targets.get(_widget_key(overlay_id, widget_id), "value")

    def tick(self) -> None:
        """Advance effect clocks through the runtime scheduler."""

        for widget_key in self._flash.tick():
            overlay_id, widget_id = self._keys.get(widget_key, ("", ""))
            if overlay_id and widget_id:
                self.effectsChanged.emit(overlay_id, widget_id)


def widget_window_data(widget_host: WidgetHostCapability, record: WidgetRecord) -> dict[str, Any]:
    """Build the widgetData payload expected by widget QML windows."""

    return widget_host.window_data(record)


def _widget_key(overlay_id: str, widget_id: str) -> str:
    return f"{overlay_id}:{widget_id}"
