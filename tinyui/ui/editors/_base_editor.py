"""Base editor classes - extracted from _editor_common.py"""

from __future__ import annotations

import time
from typing import Callable

from PySide2.QtCore import Qt
from PySide2.QtWidgets import (
    QDialogButtonBox,
    QHBoxLayout,
    QMessageBox,
    QTableWidget,
    QVBoxLayout,
)

from tinyui.backend.settings import cfg

from .._common import BaseDialog, UIScaler
from ..components.compact_button import CompactButton


def editor_button_bar(editor, left_buttons=None):
    """Build standard editor button bar.

    left_buttons: list of (label, callback) for the left side.
    Right side is always: [stretch] Apply | Save | Close
    """
    layout = QHBoxLayout()
    if left_buttons:
        for label, callback in left_buttons:
            btn = CompactButton(label)
            btn.clicked.connect(callback)
            layout.addWidget(btn)
    layout.addStretch(1)
    for label, callback in [
        ("Apply", editor.applying),
        ("Save", editor.saving),
        ("Close", editor.close),
    ]:
        btn = CompactButton(label)
        btn.clicked.connect(callback)
        layout.addWidget(btn)
    return layout


class BaseEditor(BaseDialog):
    """Base editor class with modified state tracking."""

    def __init__(self, parent):
        super().__init__(parent)
        self._is_modified = False
        self._is_rejected = False

    def confirm_discard(self) -> bool:
        """Confirm save or discard changes."""
        if not self._is_modified:
            return True

        confirm = QMessageBox.question(
            self,
            "Confirm",
            "<b>Save changes before continue?</b>",
            buttons=QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
        )

        if confirm == QMessageBox.Save:
            self.saving()
            return self.confirm_discard()

        return confirm == QMessageBox.Discard

    def is_modified(self) -> bool:
        """Is modified."""
        return self._is_modified

    def set_modified(self):
        """Set modified state."""
        if not self._is_modified:
            self._is_modified = True

    def set_unmodified(self):
        """Set unmodified state."""
        if self._is_modified:
            self._is_modified = False

    def saving(self):
        """Save changes - override in subclass."""
        pass

    def reject(self):
        """Reject(ESC) confirm."""
        if self.confirm_discard():
            self._is_rejected = True
            self.close()

    def closeEvent(self, event):
        """Close editor."""
        if self._is_rejected:
            return
        if not self.confirm_discard():
            event.ignore()

    @staticmethod
    def new_name_increment(name: str, table: QTableWidget, column: int = 0) -> str:
        """New name with number increment add at the end."""
        new_index = 1
        new_name = f"{name} {new_index}"
        exist = True
        while exist:
            items = table.findItems(new_name, Qt.MatchExactly)
            for item in items:
                if item.column() == column:
                    new_index += 1
                    new_name = f"{name} {new_index}"
                    break
            else:
                exist = False
        return new_name

    @staticmethod
    def is_value_in_table(target: str, table: QTableWidget, column: int = 0) -> bool:
        """Is there any matching value in table."""
        items = table.findItems(target, Qt.MatchExactly)
        for item in items:
            if item.column() == column:
                return True
        return False

    @staticmethod
    def reloading(reload_module: bool = True, reload_widget: bool = True) -> None:
        """Reloading module & widget only."""
        from tinyui.backend.controls import mctrl, wctrl

        if reload_module:
            mctrl.reload()
        if reload_widget:
            wctrl.reload()


class TableEditor(BaseEditor):
    """Base editor for table-based data editors."""

    def sort_rows(self, column=0):
        """Sort table rows by column."""
        if self.table.rowCount() > 1:
            self.table.sortItems(column)
            self.set_modified()

    def delete_rows(self):
        """Delete selected rows."""
        selected_rows = set(data.row() for data in self.table.selectedIndexes())
        if not selected_rows:
            QMessageBox.warning(self, "Error", "No data selected.")
            return
        if not self.confirm_operation(message="<b>Delete selected rows?</b>"):
            return
        for row_index in sorted(selected_rows, reverse=True):
            self.table.removeRow(row_index)
        self.set_modified()

    def applying(self):
        """Save & apply."""
        self.save_setting()

    def saving(self):
        """Save & close."""
        self.save_setting()
        self.accept()

    def save_setting(self):
        """Save setting: update temp, persist, wait, reload."""
        self.update_temp()
        self.persist()
        while cfg.is_saving:
            time.sleep(0.01)
        self.reloading()
        self.set_unmodified()

    def update_temp(self):
        """Read table cells back into temp data - override in subclass."""
        raise NotImplementedError

    def persist(self):
        """Write temp data to cfg and save - override in subclass."""
        raise NotImplementedError
