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

"""
Window control for PySide6 on Unix (Linux/macOS).

Qt delegates move and resize to the compositor/AppKit via
startSystemMove() / startSystemResize(). The platform handles
cursor feedback, snap and animations - no platform-specific code needed.

QML initiates drag via DragHandler.onActiveChanged -> startMove().
Resize is initiated from ResizeHandles.qml via startResize(edge).
"""

from PySide6.QtCore import Qt, Slot

from app_api.windowing.controller_api import WindowControllerApi


class WindowController(WindowControllerApi):
    """Window control for Linux/Wayland."""

    def __init__(self, window, parent=None):
        super().__init__(parent)
        self._window = window

    @Slot(float)
    def setLeftButtonWidth(self, logical_width: float) -> None:
        pass  # Not applicable - Wayland does not use hit-test zones

    @Slot()
    def toggleMaximize(self):
        if self._window.windowState() & Qt.WindowState.WindowMaximized:
            self._window.showNormal()
        else:
            self._window.showMaximized()

    @Slot()
    def minimize(self):
        self._window.showMinimized()

    @Slot()
    def startMove(self):
        """Called from QML DragHandler - compositor handles the drag."""
        self._window.startSystemMove()

    @Slot(int)
    def startResize(self, edge: int):
        """Called from ResizeHandles.qml - compositor handles the resize."""
        self._window.startSystemResize(Qt.Edge(edge))
