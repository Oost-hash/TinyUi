#
#  TinyUi - Track Notes Editor View
#  Copyright (C) 2026 Oost-hash
#
#  View layer for track/pace notes editor.
#  Uses FileService for dialogs and ViewModel for state.
#

import os
import re
from typing import List, Optional

from PySide2.QtCore import QPoint, Qt
from PySide2.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLineEdit,
    QMenu,
    QMessageBox,
    QSplitter,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from ..._common import QVAL_FILENAME, UIScaler
from ...components.compact_button import CompactButton
from ...components.table_items import FloatTableItem
from ...dialogs.track_map_viewer import MapView
from ..core.file_service import FileService
from .dialogs import BatchOffsetDialog, MetadataDialog, ReplaceDialog
from .viewmodel import TrackNotesEditorVM


class TrackNotesEditorView(QFrame):
    """Track notes editor view with map and table."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._vm: Optional[TrackNotesEditorVM] = None
        self._file_service: Optional[FileService] = None

        self.setMinimumSize(UIScaler.size(76), UIScaler.size(76))
        self._setup_ui()

    def _setup_ui(self):
        """Build UI."""
        # Status bar
        self._status_bar = QStatusBar(self)

        # Map panel
        self._map_panel = self._create_map_panel()

        # Editor panel
        self._editor_panel = self._create_editor_panel()

        # Splitter
        splitter = QSplitter(Qt.Horizontal, self)
        splitter.setHandleWidth(5)
        splitter.addWidget(self._map_panel)
        splitter.addWidget(self._editor_panel)
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)
        splitter.setStretchFactor(0, 1)

        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 0)
        layout.addWidget(splitter, stretch=1)
        layout.addWidget(self._status_bar)
        self.setLayout(layout)

    def _create_map_panel(self) -> QFrame:
        """Create map view panel."""
        self._map_view = MapView(self)
        self._map_view.reloaded.connect(self._on_map_reloaded)

        layout = QVBoxLayout()
        layout.addLayout(self._map_view.set_button_layout())
        layout.addWidget(self._map_view)
        layout.addLayout(self._map_view.set_control_layout())
        layout.setContentsMargins(0, 0, 0, 0)

        panel = QFrame(self)
        panel.setMinimumSize(UIScaler.size(38), UIScaler.size(38))
        panel.setLayout(layout)
        return panel

    def _create_editor_panel(self) -> QFrame:
        """Create editor panel with table and controls."""
        # Table
        self._table = QTableWidget(self)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._table.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self._table.setColumnWidth(0, UIScaler.size(6))
        self._table.cellChanged.connect(self._on_cell_changed)

        # Context menu
        self._table.setContextMenuPolicy(Qt.CustomContextMenu)
        self._table.customContextMenuRequested.connect(self._on_context_menu)

        # Filename
        self._filename_edit = QLineEdit()
        self._filename_edit.setValidator(QVAL_FILENAME)

        # Buttons
        self._btn_showmap = CompactButton("Hide Map")
        self._btn_showmap.clicked.connect(self._toggle_map)

        self._btn_file = CompactButton("File", has_menu=True)
        self._btn_file.setMenu(self._create_file_menu())

        self._btn_setpos = CompactButton("Set Pos", has_menu=True)
        self._btn_setpos.setMenu(self._create_setpos_menu())

        self._btn_metadata = CompactButton("Info")
        self._btn_metadata.clicked.connect(self._on_metadata)

        self._btn_save = CompactButton("Save")
        self._btn_save.clicked.connect(self._on_save)

        self._btn_add = CompactButton("Add")
        self._btn_add.clicked.connect(self._on_add)

        self._btn_insert = CompactButton("Insert")
        self._btn_insert.clicked.connect(self._on_insert)

        self._btn_sort = CompactButton("Sort")
        self._btn_sort.clicked.connect(self._on_sort)

        self._btn_delete = CompactButton("Delete")
        self._btn_delete.clicked.connect(self._on_delete)

        self._btn_replace = CompactButton("Replace")
        self._btn_replace.clicked.connect(self._on_replace)

        self._btn_offset = CompactButton("Offset")
        self._btn_offset.clicked.connect(self._on_offset)

        self._btn_close = CompactButton("Close")
        self._btn_close.clicked.connect(self.close)

        # Layouts
        top_layout = QHBoxLayout()
        top_layout.addWidget(self._btn_showmap)
        top_layout.addWidget(self._btn_file)
        top_layout.addWidget(self._filename_edit, stretch=1)
        top_layout.addWidget(self._btn_metadata)
        top_layout.addWidget(self._btn_save)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self._btn_setpos)
        btn_layout.addWidget(self._btn_add)
        btn_layout.addWidget(self._btn_insert)
        btn_layout.addWidget(self._btn_sort)
        btn_layout.addWidget(self._btn_delete)
        btn_layout.addWidget(self._btn_replace)
        btn_layout.addWidget(self._btn_offset)
        btn_layout.addStretch(1)
        btn_layout.addWidget(self._btn_close)

        editor_layout = QVBoxLayout()
        editor_layout.addLayout(top_layout)
        editor_layout.addWidget(self._table)
        editor_layout.addLayout(btn_layout)
        editor_layout.setContentsMargins(0, 0, 0, 0)

        panel = QFrame(self)
        panel.setMinimumSize(UIScaler.size(38), UIScaler.size(38))
        panel.setLayout(editor_layout)
        return panel

    def _create_file_menu(self) -> QMenu:
        """Create File menu."""
        menu = QMenu(self)

        menu.addAction("Open Pace Notes", lambda: self._open_file("Pace Notes"))
        menu.addAction("Open Track Notes", lambda: self._open_file("Track Notes"))
        menu.addSeparator()
        menu.addAction("New Pace Notes", lambda: self._new_file("Pace Notes"))
        menu.addAction("New Track Notes", lambda: self._new_file("Track Notes"))

        return menu

    def _create_setpos_menu(self) -> QMenu:
        """Create Set Pos menu."""
        menu = QMenu(self)

        menu.addAction("From Map", self._on_setpos_map)
        menu.addAction("From Telemetry", self._on_setpos_telemetry)

        return menu

    def bind_to(self, vm: TrackNotesEditorVM, file_service: FileService):
        """Bind to viewmodel and file service."""
        self._vm = vm
        self._file_service = file_service

        # Connect signals
        vm.data_changed.connect(self._refresh_table)
        vm.modified_changed.connect(self._on_modified_changed)
        vm.notes_type_changed.connect(self._on_notes_type_changed)
        vm.filename_changed.connect(self._filename_edit.setText)
        vm.positions_changed.connect(self._update_map_markers)
        vm.error_occurred.connect(self._show_error)
        vm.operation_completed.connect(self._show_success)

        # Initial load
        self._on_notes_type_changed(vm.notes_type)

    def _refresh_table(self):
        """Refresh table from VM."""
        if not self._vm:
            return

        entries = self._vm.entries
        is_pace = self._vm.notes_type == "Pace Notes"

        # Headers
        headers = ["Distance", "Note", "Call"] if is_pace else ["Distance", "Note"]
        self._table.setColumnCount(len(headers))
        self._table.setHorizontalHeaderLabels(headers)
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self._table.setColumnWidth(0, UIScaler.size(6))

        # Rows
        self._table.setRowCount(len(entries))

        for row, entry in enumerate(entries):
            # Distance
            dist_item = FloatTableItem(entry.get("distance", 0.0))
            self._table.setItem(row, 0, dist_item)

            # Note
            note_item = QTableWidgetItem(entry.get("note", ""))
            self._table.setItem(row, 1, note_item)

            # Call (pace only)
            if is_pace:
                call_item = QTableWidgetItem(entry.get("call", ""))
                self._table.setItem(row, 2, call_item)

    def _update_map_markers(self, positions: set):
        """Update map with position markers."""
        self._map_view.update_marked_coords(positions)

    def _on_cell_changed(self, row: int, col: int):
        """Handle table cell edit."""
        if not self._vm or row < 0:
            return

        item = self._table.item(row, col)
        if not item:
            return

        # Map column to field
        fields = ["distance", "note", "call"]
        field = fields[col] if col < len(fields) else "note"

        value = item.value() if col == 0 else item.text()

        self._vm.update_entry(row, field, value)

    def _on_context_menu(self, position: QPoint):
        """Show context menu."""
        # Implementatie kan later worden toegevoegd
        pass

    def _on_modified_changed(self, is_modified: bool):
        """Update save button state."""
        self._btn_save.setEnabled(is_modified)

    def _on_notes_type_changed(self, notes_type: str):
        """Update UI for notes type."""
        self._status_bar.showMessage(f"Edit Mode: {notes_type}", 0)
        self._filename_edit.setPlaceholderText(f"{notes_type} Name")
        self._refresh_table()

    def _on_add(self):
        """Add new entry."""
        if self._vm:
            idx = self._vm.add_entry()
            self._table.setCurrentCell(idx, 0)

    def _on_insert(self):
        """Insert entry at current row."""
        if not self._vm:
            return

        current = self._table.currentRow()
        idx = self._vm.insert_entry(max(0, current))
        self._table.setCurrentCell(idx, 0)

    def _on_delete(self):
        """Delete selected entries."""
        if not self._vm:
            return

        selected = set(idx.row() for idx in self._table.selectedIndexes())
        if not selected:
            QMessageBox.warning(self, "Error", "No data selected.")
            return

        if (
            QMessageBox.question(self, "Confirm", "<b>Delete selected rows?</b>")
            == QMessageBox.Yes
        ):
            self._vm.delete_entries(list(selected))

    def _on_sort(self):
        """Sort entries."""
        if self._vm:
            self._vm.sort_entries()

    def _on_offset(self):
        """Open offset dialog."""
        if not self._vm:
            return

        # Check selection
        selected = self._table.selectedIndexes()
        if not selected:
            self._show_error(
                "Select one or more values from distance column to apply offset."
            )
            return

        # Collect selected row indices
        indices = [idx.row() for idx in selected if idx.column() == 0]
        if not indices:
            self._show_error("Select values from distance column.")
            return

        # Open dialog
        def apply_offset(value: float, is_scale: bool):
            self._vm.apply_offset(indices, value, is_scale)

        dialog = BatchOffsetDialog(self, apply_offset)
        dialog.exec_()

    def _on_replace(self):
        """Open replace dialog."""
        if not self._vm:
            return

        # Get column names (skip distance)
        is_pace = self._vm.notes_type == "Pace Notes"
        column_names = ["Note", "Call"] if is_pace else ["Note"]

        def get_values(col_idx: int) -> List[str]:
            """Get unique values from column."""
            values = set()
            # Adjust column index: 0=distance, 1=note, 2=call (if pace)
            table_col = col_idx + 1  # because col_idx is 0 for note, 1 for call
            for row in range(self._table.rowCount()):
                item = self._table.item(row, table_col)
                if item:
                    values.add(item.text())
            return sorted(values)

        def do_replace(
            col_idx: int, find: str, replace: str, match_case: bool, whole_word: bool
        ):
            """Execute replace."""
            table_col = col_idx + 1
            pattern = re.escape(find)
            if whole_word:
                pattern = rf"\b{pattern}\b"
            flags = 0 if match_case else re.IGNORECASE

            for row in range(self._table.rowCount()):
                item = self._table.item(row, table_col)
                if item:
                    text = item.text()
                    new_text = re.sub(pattern, replace, text, flags=flags)
                    if new_text != text:
                        item.setText(new_text)
                        # Update VM: field name is "note" or "call"
                        field = column_names[col_idx].lower()
                        self._vm.update_entry(row, field, new_text)

        dialog = ReplaceDialog(self, column_names, get_values, do_replace)
        dialog.exec_()

    def _on_setpos_map(self):
        """Set position from map."""
        if not self._vm:
            return

        dist = self._map_view.map_seek_dist
        self._set_position_to_selected(float(dist), "from map")

    def _on_setpos_telemetry(self):
        """Set position from telemetry."""
        if not self._vm:
            return

        dist = self._vm.get_position_from_telemetry()
        if dist is not None:
            self._set_position_to_selected(dist, "from telemetry")

    def _set_position_to_selected(self, position: float, source: str):
        """Set position to selected cell."""
        selected = self._table.selectedIndexes()
        if len(selected) != 1 or selected[0].column() != 0:
            QMessageBox.warning(self, "Error", "Select one value from distance column.")
            return

        if (
            QMessageBox.question(
                self, "Confirm", f"Set position at <b>{position}</b> {source}?"
            )
            == QMessageBox.Yes
        ):
            row = selected[0].row()
            self._vm.update_entry(row, "distance", position)
            self._map_view.spinbox_pos_dist.setValue(position)
            self._map_view.update_highlighted_coords()

    def _open_file(self, notes_type: str):
        """Open file dialog and load notes."""
        if not self._confirm_discard():
            return

        directory, file_filter = self._vm.get_file_dialog_info(notes_type)
        filename_full = self._file_service.get_open_filename(
            self, f"Open {notes_type}", directory, file_filter
        )

        if filename_full:
            filepath = os.path.dirname(filename_full) + "/"
            filename = os.path.basename(filename_full)
            self._vm.load_file(filepath, filename, notes_type)

    def _new_file(self, notes_type: str):
        """Create new empty file."""
        if not self._confirm_discard():
            return

        if self._vm:
            self._vm.new_file(notes_type)

    def _on_save(self):
        """Save file."""
        if not self._vm:
            return

        if not self._vm.entries:
            self._show_error("Nothing to save.")
            return

        directory, file_filter = self._vm.get_file_dialog_info(self._vm.notes_type)
        default_name = self._vm.filename
        # Combine directory and default name for initial save path
        initial_path = (
            os.path.join(directory, default_name) if default_name else directory
        )
        full_path = self._file_service.get_save_filename(
            self, "Save Notes", initial_path, file_filter
        )

        if full_path:
            filepath = os.path.dirname(full_path) + "/"
            filename = os.path.basename(full_path)
            self._vm.filename = filename  # via setter
            self._vm.save_file(filepath)

    def _on_metadata(self):
        """Open metadata dialog."""
        if not self._vm:
            return

        def save_metadata(updated: dict):
            for key, value in updated.items():
                self._vm.update_metadata(key, value)

        dialog = MetadataDialog(self, self._vm.metadata, save_metadata)
        dialog.exec_()

    def _toggle_map(self):
        """Toggle map panel visibility."""
        if self._map_panel.isHidden():
            self._map_panel.show()
            self._btn_showmap.setText("Hide Map")
        else:
            self._map_panel.hide()
            self._btn_showmap.setText("Show Map")

    def _on_map_reloaded(self):
        """Map was reloaded."""
        if self._vm:
            self._update_map_markers(self._vm.positions)

    def _show_error(self, message: str):
        """Show error dialog."""
        QMessageBox.critical(self, "Error", message)

    def _show_success(self, message: str):
        """Show success dialog."""
        QMessageBox.information(self, "Success", message)

    def _confirm_discard(self) -> bool:
        """Confirm discard changes."""
        if not self._vm or not self._vm.is_modified:
            return True

        reply = QMessageBox.question(
            self,
            "Confirm",
            "<b>Save changes before continue?</b>",
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
        )

        if reply == QMessageBox.Save:
            self._on_save()
            return self._confirm_discard()

        return reply == QMessageBox.Discard

    def closeEvent(self, event):
        """Handle close."""
        if self._confirm_discard():
            event.accept()
        else:
            event.ignore()
