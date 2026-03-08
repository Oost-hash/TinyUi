"""Base classes and helpers shared across editors."""

from __future__ import annotations

import re
import time
from typing import Callable

from PySide2.QtCore import QRegularExpression, Qt
from PySide2.QtGui import QRegularExpressionValidator
from PySide2.QtWidgets import (
    QCheckBox,
    QComboBox,
    QCompleter,
    QDialogButtonBox,
    QDoubleSpinBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QVBoxLayout,
)

from tinyui.backend.settings import cfg
from .._common import BaseDialog, CompactButton, UIScaler


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
    """Base editor class"""

    def __init__(self, parent):
        super().__init__(parent)
        self._is_modified = False
        self._is_rejected = False

    def confirm_discard(self) -> bool:
        """Confirm save or discard changes"""
        if not self._is_modified:
            return True

        confirm = QMessageBox.question(
            self, "Confirm", "<b>Save changes before continue?</b>",
            buttons=QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)

        if confirm == QMessageBox.Save:
            self.saving()
            return self.confirm_discard()

        return confirm == QMessageBox.Discard

    def is_modified(self) -> bool:
        """Is modified"""
        return self._is_modified

    def set_modified(self):
        """Set modified state"""
        if not self._is_modified:
            self._is_modified = True

    def set_unmodified(self):
        """Set unmodified state"""
        if self._is_modified:
            self._is_modified = False

    def saving(self):
        """Save changes"""

    def reject(self):
        """Reject(ESC) confirm"""
        if self.confirm_discard():
            self._is_rejected = True
            self.close()

    def closeEvent(self, event):
        """Close editor"""
        if self._is_rejected:
            return
        if not self.confirm_discard():
            event.ignore()

    @staticmethod
    def new_name_increment(name: str, table: QTableWidget, column: int = 0) -> str:
        """New name with number increment add at the end"""
        new_index = 1
        new_name = f"{name} {new_index}"
        exist = True
        while exist:  # check existing name
            items = table.findItems(new_name, Qt.MatchExactly)
            for item in items:
                if item.column() == column:  # match column
                    new_index += 1
                    new_name = f"{name} {new_index}"
                    break
            else:
                exist = False
        return new_name

    @staticmethod
    def is_value_in_table(target: str, table: QTableWidget, column: int = 0) -> bool:
        """Is there any matching value in table"""
        items = table.findItems(target, Qt.MatchExactly)
        for item in items:
            if item.column() == column:
                return True
        return False

    @staticmethod
    def reloading(reload_module: bool = True, reload_widget: bool = True) -> None:
        """Reloading module & widget only"""
        # Delay import
        from tinyui.backend.controls import mctrl, wctrl

        if reload_module:
            mctrl.reload()
        if reload_widget:
            wctrl.reload()


class TableEditor(BaseEditor):
    """Base editor for table-based data editors.

    Subclasses must set self.table to a QTableWidget and implement:
      - refresh_table()
      - update_temp()      — read table cells back into temp data
      - persist()          — write temp to cfg and cfg.save(...)
    """

    def sort_rows(self, column=0):
        """Sort table rows by column"""
        if self.table.rowCount() > 1:
            self.table.sortItems(column)
            self.set_modified()

    def delete_rows(self):
        """Delete selected rows"""
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
        """Save & apply"""
        self.save_setting()

    def saving(self):
        """Save & close"""
        self.save_setting()
        self.accept()

    def save_setting(self):
        """Save setting: update temp, persist, wait, reload"""
        self.update_temp()
        self.persist()
        while cfg.is_saving:
            time.sleep(0.01)
        self.reloading()
        self.set_unmodified()

    def update_temp(self):
        """Read table cells back into temp data — override in subclass"""
        raise NotImplementedError

    def persist(self):
        """Write temp data to cfg and save — override in subclass"""
        raise NotImplementedError

class BatchOffset(BaseDialog):
    """Batch offset"""

    def __init__(self, parent, offset_func: Callable):
        super().__init__(parent)
        self.setWindowTitle("Batch Offset")
        self.decimals = 0
        self.value_range = 0, 1
        self.offset_func = offset_func
        self.edit_offset = QDoubleSpinBox()
        self.last_offset = QLabel("0")
        self.last_label = QLabel("Last Offset:")
        self.checkbox_scale = QCheckBox("Scale Mode")

    def config(self, decimals: int, step: float, min_range: int, max_range: int):
        """Config offset"""
        self.decimals = decimals
        self.value_range = min_range, max_range

        # Label
        layout_label = QHBoxLayout()
        layout_label.addWidget(self.last_label)
        layout_label.addStretch(1)
        layout_label.addWidget(self.last_offset)

        # Edit offset
        self.edit_offset.setDecimals(self.decimals)
        self.edit_offset.setRange(*self.value_range)
        self.edit_offset.setSingleStep(step)
        self.edit_offset.setAlignment(Qt.AlignRight)

        # Scale mode
        self.checkbox_scale.setChecked(False)
        self.checkbox_scale.toggled.connect(self.toggle_mode)

        # Button
        button_apply = QDialogButtonBox(QDialogButtonBox.Apply)
        button_apply.clicked.connect(self.applying)

        button_close = QDialogButtonBox(QDialogButtonBox.Close)
        button_close.rejected.connect(self.reject)

        layout_button = QHBoxLayout()
        layout_button.addWidget(button_apply)
        layout_button.addStretch(1)
        layout_button.addWidget(button_close)

        # Set layout
        layout_main = QVBoxLayout()
        layout_main.addLayout(layout_label)
        layout_main.addWidget(self.edit_offset)
        layout_main.addWidget(self.checkbox_scale)
        layout_main.addLayout(layout_button)
        self.setLayout(layout_main)
        self.setFixedSize(UIScaler.size(12), self.sizeHint().height())

    def toggle_mode(self, checked: bool):
        """Toggle mode"""
        self.last_offset.setText("0")
        if checked:
            self.edit_offset.setRange(0, 100)
            self.edit_offset.setDecimals(6)
            self.last_label.setText("Last Scale:")
        else:
            self.edit_offset.setRange(*self.value_range)
            self.edit_offset.setDecimals(self.decimals)
            self.last_label.setText("Last Offset:")

    def applying(self):
        """Apply offset"""
        value = self.edit_offset.value()
        if value != 0:
            self.offset_func(value, self.checkbox_scale.isChecked())
            offset_text = f"{value:.{self.edit_offset.decimals()}f}"
            self.last_offset.setText(offset_text.rstrip("0").rstrip("."))
            self.edit_offset.setValue(0)


class TableBatchReplace(BaseDialog):
    """Table batch replace"""

    def __init__(
        self, parent, table_selector: dict, table_data: QTableWidget):
        """
        Args:
            table_selector: table selector dictionary. key=column name, value=column index.
        """
        super().__init__(parent)
        self.table_selector = table_selector
        self.table_data = table_data
        self.setWindowTitle("Batch Replace")

        # Label & combobox
        self.search_selector = QComboBox()
        self.search_selector.setEditable(True)
        self.search_selector.setCompleter(QCompleter())  # disable auto-complete

        self.column_selector = QComboBox()
        self.column_selector.addItems(self.table_selector.keys())
        self.column_selector.currentIndexChanged.connect(self.update_selector)
        self.update_selector(self.table_selector[self.column_selector.currentText()])

        self.replace_entry = QLineEdit()

        self.checkbox_casematch = QCheckBox("Match Case")
        self.checkbox_casematch.setChecked(False)
        self.checkbox_exactmatch = QCheckBox("Match Whole Word")
        self.checkbox_exactmatch.setChecked(False)

        layout_option = QGridLayout()
        layout_option.setAlignment(Qt.AlignTop)
        layout_option.addWidget(QLabel("Column:"), 0, 0)
        layout_option.addWidget(QLabel("Find:"), 1, 0)
        layout_option.addWidget(QLabel("Replace:"), 2, 0)
        layout_option.addWidget(self.column_selector, 0, 1)
        layout_option.addWidget(self.search_selector, 1, 1)
        layout_option.addWidget(self.replace_entry, 2, 1)
        layout_option.addWidget(self.checkbox_exactmatch, 3, 1)
        layout_option.addWidget(self.checkbox_casematch, 4, 1)

        # Button
        button_replace = QPushButton("Replace")
        button_replace.clicked.connect(self.replacing)

        button_close = QDialogButtonBox(QDialogButtonBox.Close)
        button_close.rejected.connect(self.reject)

        layout_button = QHBoxLayout()
        layout_button.addWidget(button_replace)
        layout_button.addStretch(1)
        layout_button.addWidget(button_close)

        # Set layout
        layout_main = QVBoxLayout()
        layout_main.addLayout(layout_option)
        layout_main.addLayout(layout_button)
        self.setLayout(layout_main)
        self.setMinimumWidth(UIScaler.size(22))
        self.setFixedHeight(self.sizeHint().height())

    def update_selector(self, column_index: int, last_search: str = ""):
        """Update selector list"""
        column_index = self.table_selector[self.column_selector.currentText()]
        self.search_selector.clear()
        selector_list = set(
            self.table_data.item(row_index, column_index).text()
            for row_index in range(self.table_data.rowCount())
        )
        self.search_selector.addItems(sorted(selector_list))
        self.search_selector.setCurrentText(last_search)

    def replacing(self):
        """Replace"""
        if not self.search_selector.currentText():
            QMessageBox.warning(self, "Error", "Invalid name.")
            return

        column_index = self.table_selector[self.column_selector.currentText()]
        search = self.search_selector.currentText()
        replace = self.replace_entry.text()

        pattern = re.escape(search)  # escape special chars
        if self.checkbox_exactmatch.isChecked():
            pattern = f"^{pattern}$"

        if self.checkbox_casematch.isChecked():
            match_flag = 0
        else:
            match_flag = re.IGNORECASE

        for row_index in range(self.table_data.rowCount()):
            item = self.table_data.item(row_index, column_index)
            item.setText(re.sub(pattern, replace, item.text(), flags=match_flag))

        self.update_selector(column_index, search)
