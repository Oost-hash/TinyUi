"""List header with select-all / deselect-all buttons."""

from PySide2.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
)

from .._common import CompactButton


class ListHeader(QFrame):
    """Header bar with All / None buttons for a checkbox QListWidget.

    Args:
        parent: parent widget (must have confirm_operation method).
        title: display name for the list.
        listbox: QListWidget whose items are QCheckBox widgets.
    """

    def __init__(self, parent, title: str, listbox: QListWidget):
        super().__init__(parent)
        self._parent = parent
        self._listbox = listbox
        self._title = title

        button_selectall = CompactButton(" All ")
        button_selectall.clicked.connect(self.button_select_all)

        button_deselectall = CompactButton("None")
        button_deselectall.clicked.connect(self.button_deselect_all)

        layout = QHBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(QLabel(f"Select {title}"))
        layout.addWidget(button_selectall)
        layout.addWidget(button_deselectall)
        self.setLayout(layout)
        self.setFrameShape(QFrame.StyledPanel)

    def button_select_all(self):
        msg_text = f"Select all {self._title}s from list?"
        if self._parent.confirm_operation(message=msg_text):
            self._set_selection(True)

    def button_deselect_all(self):
        msg_text = f"Deselect all {self._title}s from list?"
        if self._parent.confirm_operation(message=msg_text):
            self._set_selection(False)

    def _set_selection(self, checked: bool):
        listbox = self._listbox
        for row_index in range(listbox.count()):
            item = listbox.item(row_index)
            listbox.itemWidget(item).setChecked(checked)
