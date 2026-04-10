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

"""Host frameless widget windows from runtime-owned widget records."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from PySide6.QtCore import QUrl
from PySide6.QtQml import QQmlComponent
from PySide6.QtQuick import QQuickWindow

from shared_runtime_host.capabilities.widget_host import WidgetHostCapability
from shared_runtime_host.capabilities.widget_api import (
    WidgetConfigWriteQmlCapability,
    WidgetEffectsQmlCapability,
    widget_window_data,
)
from runtimeV2.widgets.contracts import WidgetRecord, WidgetStatus
from ui_api.qt import create_engine

_QML_DIR = Path(__file__).resolve().parent / "qml"


@dataclass
class _HostedWidgetWindow:
    """Keep one hosted widget window together with its runtime record."""

    record: WidgetRecord
    window: QQuickWindow


class WidgetWindowHost:
    """Manage frameless widget windows for render-ready runtime records.

    Receives a runtime V2 widget config write capability that is exposed to QML
    through a small adapter so widget windows can persist their own position.
    """

    def __init__(
        self,
        widget_host: WidgetHostCapability,
        widget_config_write,
        widget_effects: WidgetEffectsQmlCapability,
    ) -> None:
        self._widget_host = widget_host
        self._widget_config_write = WidgetConfigWriteQmlCapability(widget_config_write)
        self._widget_effects = widget_effects
        self._engine = create_engine()
        self._component = QQmlComponent(
            self._engine,
            QUrl.fromLocalFile(str(_QML_DIR / "WidgetWindow.qml")),
        )
        self._windows: dict[str, _HostedWidgetWindow] = {}

    def sync_records(self, records: Sequence[WidgetRecord]) -> None:
        """Synchronize hosted windows with the given runtime records."""

        desired = {
            _record_key(record): record
            for record in records
            if record.status != WidgetStatus.IDLE
        }

        for record_key in tuple(self._windows):
            if record_key not in desired:
                hosted = self._windows.pop(record_key)
                self._widget_effects.remove_widget(hosted.record.overlay_id, hosted.record.widget_id)
                hosted.window.close()
                hosted.window.deleteLater()

        for record_key, record in desired.items():
            widget_data = widget_window_data(self._widget_host, record)
            self._widget_effects.update_widget(widget_data)
            hosted = self._windows.get(record_key)
            if hosted is None:
                obj = self._component.createWithInitialProperties(
                    {
                        "widgetData": widget_data,
                        "widgetConfigWrite": self._widget_config_write,
                        "widgetEffects": self._widget_effects,
                    }
                )
                assert obj is not None, self._component.errorString()
                assert isinstance(obj, QQuickWindow), self._component.errorString()
                self._windows[record_key] = _HostedWidgetWindow(record=record, window=obj)
                # Only show if the widget should be visible (respects global visibility toggle)
                if record.status != WidgetStatus.HIDDEN:
                    obj.show()
                continue

            hosted.record = record
            hosted.window.setProperty("widgetData", widget_data)
            hosted.window.setVisible(record.status != WidgetStatus.HIDDEN)

    def windows(self) -> tuple[QQuickWindow, ...]:
        """Return the hosted widget windows in a stable order."""

        return tuple(self._windows[record_key].window for record_key in sorted(self._windows))

    def close_all(self) -> None:
        """Close and release all hosted widget windows."""

        for hosted in self._windows.values():
            hosted.window.close()
            hosted.window.deleteLater()
        self._windows.clear()


def _record_key(record: WidgetRecord) -> str:
    return f"{record.overlay_id}:{record.widget_id}"
