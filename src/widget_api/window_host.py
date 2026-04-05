"""Host frameless widget windows from runtime-owned widget records."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from PySide6.QtCore import QUrl
from PySide6.QtQml import QQmlComponent
from PySide6.QtQuick import QQuickWindow

from runtime.widgets import WidgetRuntimeRecord, WidgetRuntimeStatus
from ui_api.qt import create_engine

_QML_DIR = Path(__file__).resolve().parent / "qml"


@dataclass
class _HostedWidgetWindow:
    """Keep one hosted widget window together with its runtime record."""

    record: WidgetRuntimeRecord
    window: QQuickWindow


class WidgetWindowHost:
    """Manage frameless widget windows for render-ready runtime records."""

    def __init__(self) -> None:
        self._engine = create_engine()
        self._component = QQmlComponent(
            self._engine,
            QUrl.fromLocalFile(str(_QML_DIR / "WidgetWindow.qml")),
        )
        self._windows: dict[str, _HostedWidgetWindow] = {}

    def sync_records(self, records: Sequence[WidgetRuntimeRecord]) -> None:
        """Synchronize hosted windows with the given runtime records."""

        desired = {
            record.widget_id: record
            for record in records
            if record.status in {WidgetRuntimeStatus.READY, WidgetRuntimeStatus.RENDERING, WidgetRuntimeStatus.HIDDEN}
        }

        for widget_id in tuple(self._windows):
            if widget_id not in desired:
                hosted = self._windows.pop(widget_id)
                hosted.window.close()
                hosted.window.deleteLater()

        for widget_id, record in desired.items():
            widget_data = _widget_data(record)
            hosted = self._windows.get(widget_id)
            if hosted is None:
                obj = self._component.createWithInitialProperties(
                    {
                        "widgetData": widget_data,
                    }
                )
                assert obj is not None, self._component.errorString()
                assert isinstance(obj, QQuickWindow), self._component.errorString()
                self._windows[widget_id] = _HostedWidgetWindow(record=record, window=obj)
                obj.show()
                continue

            hosted.record = record
            hosted.window.setProperty("widgetData", widget_data)
            hosted.window.setVisible(record.status != WidgetRuntimeStatus.HIDDEN)

    def windows(self) -> tuple[QQuickWindow, ...]:
        """Return the hosted widget windows in a stable order."""

        return tuple(self._windows[widget_id].window for widget_id in sorted(self._windows))

    def close_all(self) -> None:
        """Close and release all hosted widget windows."""

        for hosted in self._windows.values():
            hosted.window.close()
            hosted.window.deleteLater()
        self._windows.clear()


def _widget_data(record: WidgetRuntimeRecord) -> dict[str, object]:
    return {
        "widgetId": record.widget_id,
        "label": record.label,
        "source": record.source,
        "displayText": _display_text(record),
        "textColor": "#E0E0E0" if record.status != WidgetRuntimeStatus.ERROR else "#FF7A7A",
        "backgroundColor": "#CC000000",
        "visible": record.status != WidgetRuntimeStatus.HIDDEN,
        "status": record.status.value,
        "overlayId": record.overlay_id,
    }


def _display_text(record: WidgetRuntimeRecord) -> str:
    if record.status == WidgetRuntimeStatus.READY:
        return record.source
    if record.status == WidgetRuntimeStatus.RENDERING:
        return record.source
    if record.status == WidgetRuntimeStatus.WAITING_FOR_GAME:
        return "Waiting for game"
    if record.status == WidgetRuntimeStatus.WAITING_FOR_CONNECTOR:
        return "Waiting for connector"
    if record.status == WidgetRuntimeStatus.ERROR:
        return record.error_message or "Widget error"
    return ""
