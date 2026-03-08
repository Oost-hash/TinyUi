"""List header with select-all / deselect-all buttons."""

from PySide2.QtCore import Signal
from PySide2.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
)

from .compact_button import CompactButton


class ListHeader(QFrame):
    """Header bar with All / None buttons.

    Emits selectAllClicked or deselectAllClicked — parent handles the logic.
    """

    selectAllClicked = Signal()
    deselectAllClicked = Signal()

    def __init__(self, parent=None, title: str = ""):
        super().__init__(parent)

        button_selectall = CompactButton(" All ")
        button_selectall.clicked.connect(self.selectAllClicked)

        button_deselectall = CompactButton("None")
        button_deselectall.clicked.connect(self.deselectAllClicked)

        layout = QHBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(QLabel(f"Select {title}"))
        layout.addWidget(button_selectall)
        layout.addWidget(button_deselectall)
        self.setLayout(layout)
        self.setFrameShape(QFrame.StyledPanel)
