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
Wayland vensterbesturing voor PySide6 op Linux.

Qt delegeert move en resize aan de Wayland-compositor via
startSystemMove() / startSystemResize(). De compositor handelt
cursor-feedback, snap en animaties af — geen protocol-specifieke code nodig.

QML initieert drag via DragHandler.onActiveChanged → startMove().
Resize wordt gestart vanuit ResizeHandles.qml via startResize(edge).
"""

from PySide6.QtCore import QObject, Qt, Slot


class WindowController(QObject):
    """Vensterbesturing voor Linux/Wayland."""

    def __init__(self, window, parent=None):
        super().__init__(parent)
        self._window = window

    @Slot(float)
    def setLeftButtonWidth(self, logical_width: float) -> None:
        pass  # Niet van toepassing — Wayland gebruikt geen hit-test zones

    @Slot()
    def toggleMaximize(self):
        if self._window.windowState() & Qt.WindowMaximized:
            self._window.showNormal()
        else:
            self._window.showMaximized()

    @Slot()
    def minimize(self):
        self._window.showMinimized()

    @Slot()
    def startMove(self):
        """Aangeroepen vanuit QML DragHandler — compositor handelt de drag af."""
        self._window.startSystemMove()

    @Slot(int)
    def startResize(self, edge: int):
        """Aangeroepen vanuit ResizeHandles.qml — compositor handelt de resize af."""
        self._window.startSystemResize(Qt.Edge(edge))
