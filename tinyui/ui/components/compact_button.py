"""Compact auto-sized button component."""

from PySide2.QtWidgets import QPushButton

from .. import UIScaler


class CompactButton(QPushButton):
    """Compact button style"""

    def __init__(self, text, parent=None, has_menu=False):
        super().__init__(text, parent)
        self.setFixedWidth(
            self.fontMetrics().boundingRect(text).width()
            + UIScaler.FONT_PIXEL_SCALED * (1 + has_menu)
        )
