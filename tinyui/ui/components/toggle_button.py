"""Checkable toggle button with two text labels."""

from PySide2.QtWidgets import QPushButton


class ToggleButton(QPushButton):
    """Checkable QPushButton that shows different text when on/off.

    Args:
        on_text: text shown when checked.
        off_text: text shown when unchecked.
        parent: optional parent widget.
    """

    def __init__(self, on_text: str = "ON", off_text: str = "OFF", parent=None):
        super().__init__(parent)
        self._on_text = on_text
        self._off_text = off_text
        self.setCheckable(True)
        self.toggled.connect(self._update_text)
        self._update_text(self.isChecked())

    def _update_text(self, checked: bool):
        self.setText(self._on_text if checked else self._off_text)
