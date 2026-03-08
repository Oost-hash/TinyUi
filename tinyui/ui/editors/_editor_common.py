"""Editor helpers - dialogs and utilities."""

from __future__ import annotations

import re
from typing import Callable

from PySide2.QtCore import Qt
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
    QPushButton,
)

from .._common import BaseDialog, UIScaler
from ..components.compact_button import CompactButton


class BatchOffset(BaseDialog):
    """Batch offset dialog."""

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
        """Config offset."""
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
        """Toggle mode."""
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
        """Apply offset."""
        value = self.edit_offset.value()
        if value != 0:
            self.offset_func(value, self.checkbox_scale.isChecked())
            offset_text = f"{value:.{self.edit_offset.decimals()}f}"
            self.last_offset.setText(offset_text.rstrip("0").rstrip("."))
            self.edit_offset.setValue(0)


class TableBatchReplace(BaseDialog):
    """Table batch replace dialog."""

    def __init__(self, parent, table_selector: dict, table_data):
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
        """Update selector list."""
        column_index = self.table_selector[self.column_selector.currentText()]
        self.search_selector.clear()
        selector_list = set(
            self.table_data.item(row_index, column_index).text()
            for row_index in range(self.table_data.rowCount())
        )
        self.search_selector.addItems(sorted(selector_list))
        self.search_selector.setCurrentText(last_search)

    def replacing(self):
        """Replace."""
        if not self.search_selector.currentText():
            QMessageBox.warning(self, "Error", "Invalid name.")
            return

        column_index = self.table_selector[self.column_selector.currentText()]
        search = self.search_selector.currentText()
        replace = self.replace_entry.text()

        pattern = re.escape(search)
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
