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

import os
import sys

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget


def _images_dir() -> str:
    if getattr(sys, "frozen", False):
        return os.path.join(os.path.dirname(sys.executable), "images")
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "images")


class TitleBar(QWidget):
    """Custom title bar component voor frameless windows."""

    def __init__(self, title: str = "", parent=None, closable=True, minimizable=False, maximizable=True, icon: QIcon = None):
        super().__init__(parent)
        self.setObjectName("titleBar")
        self.setFixedHeight(36)
        self._drag_pos = None
        self._icon_size = QSize(14, 14)
        self._maximizable = maximizable

        images = _images_dir()
        self._maximize_icon = QIcon(os.path.join(images, "maximize.svg"))
        self._restore_icon = QIcon(os.path.join(images, "restore.svg"))

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 0, 4, 0)
        layout.setSpacing(6)

        if icon:
            icon_label = QLabel()
            icon_label.setPixmap(icon.pixmap(28, 28))
            icon_label.setObjectName("titleBarIcon")
            icon_label.setFixedSize(28, 28)
            layout.addWidget(icon_label)

        self._title = QLabel(title)
        self._title.setObjectName("titleBarLabel")
        layout.addWidget(self._title)
        layout.addStretch()

        if minimizable:
            min_btn = QPushButton()
            min_btn.setObjectName("titleBarBtn")
            min_btn.setIcon(QIcon(os.path.join(images, "minimize.svg")))
            min_btn.setIconSize(self._icon_size)
            min_btn.setFixedSize(32, 28)
            min_btn.clicked.connect(lambda: self.window().showMinimized())
            layout.addWidget(min_btn)

        if maximizable:
            self._max_btn = QPushButton()
            self._max_btn.setObjectName("titleBarBtn")
            self._max_btn.setIcon(self._maximize_icon)
            self._max_btn.setIconSize(self._icon_size)
            self._max_btn.setFixedSize(32, 28)
            self._max_btn.clicked.connect(self._toggle_maximize)
            layout.addWidget(self._max_btn)

        if closable:
            close_btn = QPushButton()
            close_btn.setObjectName("titleBarCloseBtn")
            close_btn.setIcon(QIcon(os.path.join(images, "close.svg")))
            close_btn.setIconSize(self._icon_size)
            close_btn.setFixedSize(32, 28)
            close_btn.clicked.connect(lambda: self.window().close())
            layout.addWidget(close_btn)

    def set_title(self, title: str):
        self._title.setText(title)

    def _toggle_maximize(self):
        win = self.window()
        if win.isMaximized():
            win.showNormal()
            self._max_btn.setIcon(self._maximize_icon)
        else:
            win.showMaximized()
            self._max_btn.setIcon(self._restore_icon)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.window().frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() & Qt.LeftButton:
            self.window().move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton and self._maximizable:
            self._toggle_maximize()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
