"""Combo box with action buttons."""

from PySide2.QtWidgets import QComboBox, QHBoxLayout, QWidget

from .compact_button import CompactButton


class SelectorBar(QWidget):
    """QComboBox + action buttons in a horizontal layout.

    Access the combo box directly via self.combo.
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
