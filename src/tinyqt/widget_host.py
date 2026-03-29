"""Shared tinyqt widget-surface hosting.

The host layer owns top-level widget windows. Widget packages still own the
context objects and widget editing logic.
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QColor, QFont, QMouseEvent, QPainter, QPaintEvent, QPen
from PySide6.QtWidgets import QWidget

from tinyruntime_schema import get_logger
from tinycore.paths import AppPaths

_log = get_logger(__name__)


@dataclass(frozen=True)
class WidgetSurfacePaths:
    @classmethod
    def from_app_paths(cls, paths: AppPaths) -> "WidgetSurfacePaths":
        if paths.source_root is None:
            raise RuntimeError("Widget surface hosting requires source_root in source mode")
        return cls()


class _WidgetSurfaceWindow(QWidget):
    def __init__(self, *, widget_context: object, overlay_state: object) -> None:
        super().__init__(None)
        self._widget_context = widget_context
        self._overlay_state = overlay_state
        self._drag_offset = QPoint()
        self._dragging = False

        self.setWindowFlags(
            Qt.WindowType.Tool
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedSize(120, 56)

        for signal_name in (
            "stateChanged",
            "positionChanged",
            "configChanged",
            "demoChanged",
        ):
            signal = getattr(widget_context, signal_name, None)
            if signal is not None:
                signal.connect(self._sync_from_state)

        for signal_name in ("overlayVisibleChanged", "previewWidgetChanged"):
            signal = getattr(overlay_state, signal_name, None)
            if signal is not None:
                signal.connect(self._sync_from_state)

        self._sync_from_state()

    def _ctx(self, name: str, default=None):
        return getattr(self._widget_context, name, default)

    def _overlay(self, name: str, default=None):
        return getattr(self._overlay_state, name, default)

    def _ctx_int(self, name: str, default: int = 0) -> int:
        value = self._ctx(name, default)
        return int(default if value is None else value)

    def _sync_from_state(self) -> None:
        self.move(self._ctx_int("widgetX"), self._ctx_int("widgetY"))

        flash_target = str(self._ctx("flashTarget", "value"))
        flash_visible = bool(self._ctx("textVisible", True))
        if flash_target == "widget":
            self.setWindowOpacity(1.0 if flash_visible else 0.0)
        else:
            self.setWindowOpacity(1.0)

        preview_widget_id = str(self._overlay("previewWidgetId", ""))
        widget_id = str(self._ctx("widgetId", ""))
        overlay_visible = bool(self._overlay("overlayVisible", True))
        enabled = bool(self._ctx("enabled", False))
        should_show = preview_widget_id == widget_id or (overlay_visible and enabled)
        self.setVisible(should_show)
        self.update()

    def paintEvent(self, _event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(0, 0, 0, 204))
        painter.drawRoundedRect(self.rect(), 6, 6)

        border_color = QColor(str(self._ctx("color", "#E0E0E0")))
        border_pen = QPen(border_color, 2 if bool(self._ctx("enabled", False)) else 1)
        painter.setPen(border_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 6, 6)

        flash_target = str(self._ctx("flashTarget", "value"))
        flash_visible = bool(self._ctx("textVisible", True))
        text_opacity = 1.0
        value_opacity = 1.0
        if flash_target == "text":
            text_opacity = 1.0 if flash_visible else 0.0
            value_opacity = text_opacity
        elif flash_target == "value":
            value_opacity = 1.0 if flash_visible else 0.0

        label_rect = self.rect().adjusted(8, 8, -8, -28)
        value_rect = self.rect().adjusted(8, 24, -8, -8)

        painter.setPen(QColor("#888888"))
        painter.setOpacity(text_opacity)
        label_font = QFont("Segoe UI", 10)
        painter.setFont(label_font)
        painter.drawText(label_rect, int(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop), str(self._ctx("label", "")))

        painter.setPen(border_color)
        painter.setOpacity(value_opacity)
        value_font = QFont("Segoe UI", 22)
        value_font.setBold(True)
        painter.setFont(value_font)
        painter.drawText(value_rect, int(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom), str(self._ctx("text", "")))

        painter.end()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() != Qt.MouseButton.LeftButton:
            return
        self._dragging = True
        self._drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
        event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if not self._dragging:
            return
        self.move(event.globalPosition().toPoint() - self._drag_offset)
        event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() != Qt.MouseButton.LeftButton:
            return
        self._dragging = False
        move_slot = getattr(self._widget_context, "move", None)
        if callable(move_slot):
            move_slot(int(self.x()), int(self.y()))
        event.accept()


class WidgetSurfaceHost:
    """Host one top-level Qt window per widget context."""

    def __init__(self, *, paths: WidgetSurfacePaths, model: object, overlay_state: object) -> None:
        self._paths = paths
        self._model = model
        self._overlay_state = overlay_state
        self._windows: list[_WidgetSurfaceWindow] = []
        self._started = False

    def start(self) -> None:
        if self._started:
            return
        self._create_windows()
        self._started = True

    def stop(self) -> None:
        for window in self._windows:
            try:
                window.close()
                window.deleteLater()
            except RuntimeError:
                pass
        self._windows.clear()
        self._started = False

    def _create_windows(self) -> None:
        contexts_attr = getattr(self._model, "contexts", None)
        contexts = contexts_attr() if callable(contexts_attr) else contexts_attr
        if not isinstance(contexts, list):
            raise RuntimeError("widget surface host expected WidgetModel.contexts to be a list")

        for widget_context in contexts:
            window = _WidgetSurfaceWindow(
                widget_context=widget_context,
                overlay_state=self._overlay_state,
            )
            window.show()
            self._windows.append(window)

        _log.overlay("widget surface host started", widgets=len(self._windows))
