import os
import sys

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton


def _images_dir() -> str:
    """Bepaal het pad naar de map met afbeeldingen."""
    if getattr(sys, "frozen", False):
        return os.path.join(os.path.dirname(sys.executable), "images")
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "images")


class TitleBar(QFrame):
    """Custom title bar component voor frameless windows."""

    def __init__(
        self,
        title: str = "",
        parent=None,
        closable=True,
        minimizable=False,
        maximizable=True,
        icon: QIcon = None,
    ):
        super().__init__(parent)
        self.setObjectName("titleBar")
        self.setAutoFillBackground(True)
        self.setFocusPolicy(Qt.NoFocus)
        self.setFixedHeight(36)
        self._maximizable = maximizable

        images = _images_dir()
        self._maximize_icon = QIcon(os.path.join(images, "maximize.svg"))
        self._restore_icon = QIcon(os.path.join(images, "restore.svg"))

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 0, 4, 0)
        layout.setSpacing(6)

        # Applicatie-icoon (optioneel)
        if icon:
            icon_label = QLabel()
            icon_label.setPixmap(icon.pixmap(28, 28))
            icon_label.setObjectName("titleBarIcon")
            icon_label.setFixedSize(28, 28)
            layout.addWidget(icon_label)

        # Titel
        self._title = QLabel(title)
        self._title.setObjectName("titleBarLabel")
        layout.addWidget(self._title)
        layout.addStretch()

        # Minimaliseerknop
        if minimizable:
            min_btn = QPushButton()
            min_btn.setObjectName("titleBarBtn")
            min_btn.setIcon(QIcon(os.path.join(images, "minimize.svg")))
            min_btn.setIconSize(QSize(14, 14))
            min_btn.setFixedSize(32, 28)
            min_btn.clicked.connect(lambda: self.window().showMinimized())
            layout.addWidget(min_btn)

        # Maximaliseer/herstelknop
        if maximizable:
            self._max_btn = QPushButton()
            self._max_btn.setObjectName("titleBarBtn")
            self._max_btn.setIcon(self._maximize_icon)
            self._max_btn.setIconSize(QSize(14, 14))
            self._max_btn.setFixedSize(32, 28)
            self._max_btn.clicked.connect(self._toggle_maximize)
            layout.addWidget(self._max_btn)

        # Sluitknop
        if closable:
            close_btn = QPushButton()
            close_btn.setObjectName("titleBarCloseBtn")
            close_btn.setIcon(QIcon(os.path.join(images, "close.svg")))
            close_btn.setIconSize(QSize(14, 14))
            close_btn.setFixedSize(32, 28)
            close_btn.clicked.connect(lambda: self.window().close())
            layout.addWidget(close_btn)

    def set_title(self, title: str):
        """Wijzig de titel van de titelbalk."""
        self._title.setText(title)

    def update_maximize_icon(self, maximized: bool):
        if hasattr(self, "_max_btn"):
            if maximized:
                self._max_btn.setIcon(self._restore_icon)
            else:
                self._max_btn.setIcon(self._maximize_icon)

    def _toggle_maximize(self):
        win = self.window()
        if win.isMaximized():
            win.showNormal()
        else:
            win.showMaximized()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            win = self.window()
            if win.isMaximized():
                win.showNormal()
            if win.windowHandle():
                win.windowHandle().startSystemMove()
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton and self._maximizable:
            self._toggle_maximize()
            event.accept()
