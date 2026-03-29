from __future__ import annotations

from collections import defaultdict
from typing import Any, cast

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QTabWidget,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from tinydevtools.runtime_viewmodel import RuntimeViewModel
from tinydevtools.state_monitor_viewmodel import StateMonitorViewModel

RuntimeViewModelClass = cast(Any, RuntimeViewModel)
StateMonitorViewModelClass = cast(Any, StateMonitorViewModel)


def _with_alpha(color: str, alpha: float) -> str:
    tint = QColor(color)
    tint.setAlphaF(max(0.0, min(1.0, alpha)))
    return tint.name(QColor.NameFormat.HexArgb)


class NativeDevToolsWindow(QWidget):
    """Native Qt devtools window used for the separate TinyUI diagnostics surface."""

    def __init__(self, *, core, theme, log_inspector) -> None:
        super().__init__(None, Qt.WindowType.Window)
        self._core = core
        self._theme = theme
        self._log_inspector = log_inspector
        self._runtime_vm = RuntimeViewModelClass(core)
        if core.runtime_inspector is None:
            raise RuntimeError("CoreRuntime does not have a runtime_inspector attached")
        self._state_vm = StateMonitorViewModelClass(core.runtime_inspector)
        for context in getattr(core.overlay.model, "contexts", []):
            self._state_vm.register_object(f"Widget: {context.title}", context)

        self._console_debug = True
        self._console_info = True
        self._console_warning = True
        self._console_error = True
        self._last_log_count = 0

        self.setWindowTitle("Dev Tools")
        self.resize(980, 680)
        self.setMinimumSize(720, 480)
        self.setObjectName("NativeDevToolsWindow")

        self._tabs = QTabWidget()
        self._tabs.setDocumentMode(True)
        self._tabs.setTabPosition(QTabWidget.TabPosition.North)

        self._build_state_tab()
        self._build_runtime_tab()
        self._build_console_tab()

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(16, 16, 16, 16)
        root_layout.setSpacing(0)
        root_layout.addWidget(self._tabs)

        self._refresh_timer = QTimer(self)
        self._refresh_timer.setInterval(250)
        self._refresh_timer.timeout.connect(self._refresh_views)

        self._apply_theme()
        theme.changed.connect(self._apply_theme)

    def _build_state_tab(self) -> None:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        toolbar = QFrame()
        toolbar.setObjectName("DevToolsToolbar")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(10, 8, 10, 8)
        toolbar_layout.setSpacing(8)

        self._state_source_combo = QComboBox()
        self._state_source_combo.currentIndexChanged.connect(self._select_state_source)
        self._state_copy_all_button = QPushButton("Copy all")
        self._state_copy_all_button.clicked.connect(self._state_vm.copyAllEntries)
        self._state_capture_button = QPushButton("Record")
        self._state_capture_button.clicked.connect(self._toggle_state_capture)
        self._state_copy_path_button = QPushButton("Copy path")
        self._state_copy_path_button.clicked.connect(self._state_vm.copyCapturePath)

        toolbar_layout.addWidget(self._state_source_combo, 1)
        toolbar_layout.addWidget(self._state_copy_all_button)
        toolbar_layout.addWidget(self._state_capture_button)
        toolbar_layout.addWidget(self._state_copy_path_button)

        self._state_tree = QTreeWidget()
        self._state_tree.setObjectName("DevToolsTree")
        self._state_tree.setColumnCount(2)
        self._state_tree.setHeaderLabels(["Key", "Value"])
        self._state_tree.setRootIsDecorated(False)
        self._state_tree.setAlternatingRowColors(True)
        self._state_tree.itemClicked.connect(self._handle_state_item_click)

        layout.addWidget(toolbar)
        layout.addWidget(self._state_tree, 1)
        self._tabs.addTab(page, "State")

    def _build_runtime_tab(self) -> None:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        toolbar = QFrame()
        toolbar.setObjectName("DevToolsToolbar")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(10, 8, 10, 8)
        toolbar_layout.setSpacing(8)

        self._runtime_summary = QLabel("No runtime data")
        self._runtime_summary.setObjectName("SummaryLabel")
        self._runtime_copy_button = QPushButton("Copy all")
        self._runtime_copy_button.clicked.connect(self._runtime_vm.copyOverview)

        toolbar_layout.addWidget(self._runtime_summary, 1)
        toolbar_layout.addWidget(self._runtime_copy_button)

        self._runtime_tree = QTreeWidget()
        self._runtime_tree.setObjectName("DevToolsTree")
        self._runtime_tree.setColumnCount(5)
        self._runtime_tree.setHeaderLabels(["Unit", "State", "Kind", "Execution", "Parent"])
        self._runtime_tree.setAlternatingRowColors(True)

        layout.addWidget(toolbar)
        layout.addWidget(self._runtime_tree, 1)
        self._tabs.addTab(page, "Runtime")

    def _build_console_tab(self) -> None:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        toolbar = QFrame()
        toolbar.setObjectName("DevToolsToolbar")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(10, 8, 10, 8)
        toolbar_layout.setSpacing(8)

        self._debug_check = QCheckBox("Debug")
        self._debug_check.setChecked(True)
        self._debug_check.toggled.connect(self._set_console_debug)
        self._info_check = QCheckBox("Info")
        self._info_check.setChecked(True)
        self._info_check.toggled.connect(self._set_console_info)
        self._warning_check = QCheckBox("Warning")
        self._warning_check.setChecked(True)
        self._warning_check.toggled.connect(self._set_console_warning)
        self._error_check = QCheckBox("Error")
        self._error_check.setChecked(True)
        self._error_check.toggled.connect(self._set_console_error)
        self._console_clear_button = QPushButton("Clear")
        self._console_clear_button.clicked.connect(self._clear_console)

        toolbar_layout.addWidget(self._debug_check)
        toolbar_layout.addWidget(self._info_check)
        toolbar_layout.addWidget(self._warning_check)
        toolbar_layout.addWidget(self._error_check)
        toolbar_layout.addStretch(1)
        toolbar_layout.addWidget(self._console_clear_button)

        self._console = QPlainTextEdit()
        self._console.setObjectName("ConsoleOutput")
        self._console.setReadOnly(True)

        layout.addWidget(toolbar)
        layout.addWidget(self._console, 1)
        self._tabs.addTab(page, "Console")

    def _apply_theme(self) -> None:
        self.setStyleSheet(
            f"""
            QWidget#NativeDevToolsWindow {{
                background-color: {self._theme.surface};
                color: {self._theme.text};
                font-family: "{self._theme.fontFamily}";
                font-size: {self._theme.fontSizeBase}px;
            }}
            QTabWidget::pane {{
                border: 1px solid {self._theme.border};
                background-color: {self._theme.surface};
                top: -1px;
            }}
            QTabBar::tab {{
                background-color: {self._theme.surfaceAlt};
                color: {self._theme.textSecondary};
                border: 1px solid {self._theme.border};
                padding: 8px 14px;
                margin-right: 4px;
                min-width: 96px;
            }}
            QTabBar::tab:selected {{
                background-color: {self._theme.surfaceRaised};
                color: {self._theme.text};
                border-color: {self._theme.accent};
            }}
            QTabBar::tab:hover:!selected {{
                background-color: {_with_alpha(self._theme.accent, 0.08)};
                color: {self._theme.text};
            }}
            QFrame#DevToolsToolbar {{
                background-color: {self._theme.surfaceAlt};
                border: 1px solid {self._theme.border};
            }}
            QLabel#SummaryLabel {{
                color: {self._theme.textSecondary};
                font-size: {self._theme.fontSizeSmall}px;
            }}
            QTreeWidget#DevToolsTree, QPlainTextEdit#ConsoleOutput {{
                background-color: {self._theme.surfaceAlt};
                border: 1px solid {self._theme.border};
                alternate-background-color: {_with_alpha(self._theme.surface, 0.18)};
            }}
            QHeaderView::section {{
                background-color: {self._theme.surfaceRaised};
                color: {self._theme.textMuted};
                border: none;
                border-bottom: 1px solid {self._theme.border};
                padding: 6px 8px;
                font-weight: 600;
            }}
            QPushButton {{
                background-color: {self._theme.surfaceFloating};
                border: 1px solid {self._theme.border};
                color: {self._theme.textSecondary};
                padding: 6px 12px;
                min-width: 82px;
            }}
            QPushButton:hover {{
                background-color: {self._theme.surfaceRaised};
                color: {self._theme.text};
            }}
            QComboBox {{
                background-color: {self._theme.surfaceFloating};
                border: 1px solid {self._theme.border};
                padding: 6px 8px;
                min-height: 28px;
            }}
            QComboBox:focus {{
                border-color: {self._theme.accent};
            }}
            QCheckBox {{
                color: {self._theme.textSecondary};
                spacing: 6px;
            }}
            QCheckBox::indicator {{
                width: 14px;
                height: 14px;
            }}
            QCheckBox::indicator:unchecked {{
                background-color: {self._theme.surfaceFloating};
                border: 1px solid {self._theme.border};
            }}
            QCheckBox::indicator:checked {{
                background-color: {self._theme.accent};
                border: 1px solid {self._theme.accent};
            }}
            QPlainTextEdit#ConsoleOutput {{
                color: {self._theme.text};
                selection-background-color: {_with_alpha(self._theme.accent, 0.18)};
            }}
            """
        )

    def open_window(self) -> None:
        self._state_vm.start()
        self._runtime_vm.start()
        self._refresh_timer.start()
        self._refresh_views()
        self.show()
        self.raise_()
        self.activateWindow()

    def toggle(self) -> None:
        if self.isVisible():
            self.hide()
            self._refresh_timer.stop()
            self._state_vm.shutdown()
            self._runtime_vm.shutdown()
            return
        self.open_window()

    def closeEvent(self, event) -> None:  # type: ignore[override]
        self._refresh_timer.stop()
        self._state_vm.shutdown()
        self._runtime_vm.shutdown()
        super().closeEvent(event)

    def _select_state_source(self, index: int) -> None:
        self._state_vm.selectSource(index)
        self._refresh_state_view()

    def _toggle_state_capture(self) -> None:
        self._state_vm.toggleCapture()
        self._refresh_state_toolbar()

    def _handle_state_item_click(self, item: QTreeWidgetItem, column: int) -> None:
        if item.childCount() > 0:
            section_name = item.data(0, Qt.ItemDataRole.UserRole)
            if isinstance(section_name, str):
                self._state_vm.toggleSection(section_name)
                self._refresh_state_view()
            return
        if column == 1:
            key = item.data(0, Qt.ItemDataRole.UserRole)
            value = item.text(1)
            if isinstance(key, str):
                self._state_vm.copyEntry(key, value)

    def _set_console_debug(self, checked: bool) -> None:
        self._console_debug = checked
        self._refresh_console_view()

    def _set_console_info(self, checked: bool) -> None:
        self._console_info = checked
        self._refresh_console_view()

    def _set_console_warning(self, checked: bool) -> None:
        self._console_warning = checked
        self._refresh_console_view()

    def _set_console_error(self, checked: bool) -> None:
        self._console_error = checked
        self._refresh_console_view()

    def _clear_console(self) -> None:
        self._log_inspector.clear()
        self._last_log_count = 0
        self._refresh_console_view()

    def _refresh_views(self) -> None:
        self._refresh_state_view()
        self._refresh_runtime_view()
        self._refresh_console_view()

    def _refresh_state_toolbar(self) -> None:
        capture_active = self._state_vm.captureActive
        self._state_capture_button.setText("Recording" if capture_active else "Record")
        self._state_copy_path_button.setEnabled(capture_active)
        self._state_copy_all_button.setEnabled(bool(self._state_vm.entries))

    def _refresh_state_view(self) -> None:
        sources = self._state_vm.sources
        selected = self._state_vm.selectedIndex
        self._state_source_combo.blockSignals(True)
        self._state_source_combo.clear()
        for source in sources:
            self._state_source_combo.addItem(str(source["label"]))
        if 0 <= selected < self._state_source_combo.count():
            self._state_source_combo.setCurrentIndex(selected)
        self._state_source_combo.blockSignals(False)

        grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
        for entry in self._state_vm.entries:
            key = str(entry["key"])
            section, _, leaf = key.partition(".")
            if not leaf:
                section = "general"
                leaf = key
            grouped[section].append(
                {
                    "fullKey": key,
                    "key": leaf,
                    "value": str(entry["value"]),
                }
            )

        self._state_tree.clear()
        for section_name, entries in grouped.items():
            section_item = QTreeWidgetItem(
                [section_name.replace("_", " ").title(), f"{len(entries)} item(s)"]
            )
            section_item.setData(0, Qt.ItemDataRole.UserRole, section_name)
            section_item.setFirstColumnSpanned(True)
            section_item.setExpanded(True)
            section_item.setForeground(0, QColor(self._theme.text))
            section_item.setForeground(1, QColor(self._theme.textMuted))
            self._state_tree.addTopLevelItem(section_item)
            for entry in entries:
                child = QTreeWidgetItem([str(entry["key"]), str(entry["value"])])
                child.setData(0, Qt.ItemDataRole.UserRole, entry["fullKey"])
                child.setForeground(0, QColor(self._theme.textSecondary))
                child.setForeground(1, QColor(self._theme.text))
                section_item.addChild(child)

        self._state_tree.expandAll()
        self._refresh_state_toolbar()

    def _refresh_runtime_view(self) -> None:
        self._runtime_summary.setText(self._runtime_vm.summary or "No runtime data")
        self._runtime_tree.clear()
        items_by_id: dict[str, QTreeWidgetItem] = {}
        for unit in self._runtime_vm.units:
            unit_id = str(unit["id"])
            parent_id = str(unit["parent"])
            row = [
                str(unit.get("displayId", unit_id)),
                str(unit["state"]),
                str(unit["kind"]),
                str(unit["execution"]),
                parent_id,
            ]
            item = QTreeWidgetItem(row)
            item.setForeground(0, QColor(self._theme.text))
            item.setForeground(1, QColor(self._theme.accent if str(unit["state"]) == "running" else self._theme.textSecondary))
            item.setForeground(2, QColor(self._theme.textSecondary))
            item.setForeground(3, QColor(self._theme.textSecondary))
            item.setForeground(4, QColor(self._theme.textMuted))
            if parent_id and parent_id in items_by_id:
                items_by_id[parent_id].addChild(item)
            else:
                self._runtime_tree.addTopLevelItem(item)
            items_by_id[unit_id] = item
        self._runtime_tree.expandAll()
        self._runtime_copy_button.setEnabled(bool(self._runtime_vm.units))

    def _log_visible(self, level: str) -> bool:
        if level == "DEBUG":
            return self._console_debug
        if level == "INFO":
            return self._console_info
        if level == "WARNING":
            return self._console_warning
        return self._console_error

    def _refresh_console_view(self) -> None:
        records = [
            entry
            for entry in self._log_inspector.records()
            if self._log_visible(entry.level)
        ]
        self._last_log_count = len(records)
        lines = [f"{entry.time}  {entry.level:<8}  {entry.name}  {entry.message}" for entry in records]
        self._console.setPlainText("\n".join(lines))
        cursor = self._console.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self._console.setTextCursor(cursor)
