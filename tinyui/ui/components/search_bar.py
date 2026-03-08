"""Search bar with autocomplete and clear button."""

from PySide2.QtCore import Qt
from PySide2.QtWidgets import (
    QCompleter,
    QHBoxLayout,
    QLineEdit,
    QWidget,
)

from ..components.compact_button import CompactButton


class SearchBar(QWidget):
    """QLineEdit + clear button + optional QCompleter.

    Attributes:
        textChanged: forwarded from the inner QLineEdit.
    """

    def __init__(self, parent=None, placeholder: str = "", word_set=None):
        super().__init__(parent)
        self._edit = QLineEdit(self)
        self._edit.setPlaceholderText(placeholder)

        if word_set is not None:
            completer = QCompleter(word_set, self)
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            self._edit.setCompleter(completer)

        button_clear = CompactButton("Clear")
        button_clear.clicked.connect(self._edit.clear)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._edit, stretch=1)
        layout.addWidget(button_clear)
        self.setLayout(layout)

        # Forward signal
        self.textChanged = self._edit.textChanged
