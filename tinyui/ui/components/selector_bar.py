"""Combo box with action buttons."""

from PySide2.QtWidgets import QComboBox, QHBoxLayout, QWidget

from .._common import CompactButton


class SelectorBar(QWidget):
    """QComboBox + action buttons in a horizontal layout.

    Args:
        parent: parent widget.
        buttons: list of (label, callback) tuples for action buttons.
    """

    def __init__(self, parent=None, buttons: list[tuple[str, object]] = ()):
        super().__init__(parent)
        self.combo = QComboBox()

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.combo, stretch=1)

        for label, callback in buttons:
            btn = CompactButton(label)
            btn.clicked.connect(callback)
            layout.addWidget(btn)

        self.setLayout(layout)

    # Convenience forwards
    def addItems(self, items):
        self.combo.addItems(items)

    def addItem(self, item):
        self.combo.addItem(item)

    def currentText(self):
        return self.combo.currentText()

    def currentIndex(self):
        return self.combo.currentIndex()

    def setCurrentText(self, text):
        self.combo.setCurrentText(text)

    def removeItem(self, index):
        self.combo.removeItem(index)
