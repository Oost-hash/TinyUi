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
    QSizePolicy,
    QScrollArea,
    QTabWidget,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from tinydevtools.button_actions import (
    build_console_toolbar_actions,
    build_devtools_button_actions,
    build_runtime_toolbar_actions,
    build_state_toolbar_actions,
)
from tinydevtools.log_settings_viewmodel import LogSettingsViewModel
from tinydevtools.runtime_viewmodel import RuntimeViewModel
from tinydevtools.state_monitor_viewmodel import StateMonitorViewModel
from tinyqt_native.native_tool_window import NativeToolWindowBase, with_alpha

LogSettingsViewModelClass = cast(Any, LogSettingsViewModel)
RuntimeViewModelClass = cast(Any, RuntimeViewModel)
StateMonitorViewModelClass = cast(Any, StateMonitorViewModel)


class NativeDevToolsWindow(NativeToolWindowBase):
    """Native Qt devtools window used for the separate TinyUI diagnostics surface."""

    def __init__(self, *, core, theme, log_inspector, manifest) -> None:
        super().__init__(
            title=manifest.title,
            eyebrow=manifest.window.eyebrow or "DEVTOOLS",
            subtitle=manifest.window.subtitle,
            theme=theme,
            object_name="NativeDevToolsWindow",
            width=manifest.window.default_width,
            height=manifest.window.default_height,
            min_width=manifest.window.min_width,
            min_height=manifest.window.min_height,
        )
        self._core = core
        self._theme = theme
        self._manifest = manifest
        self._log_inspector = log_inspector
        self._log_settings_vm = LogSettingsViewModelClass()
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
        self._console_auto_scroll = True
        self._last_log_count = 0

        self._tabs = QTabWidget()
        self._tabs.setDocumentMode(True)
        self._tabs.setTabPosition(QTabWidget.TabPosition.North)
        self._tabs.currentChanged.connect(self._update_header_copy)

        self._build_state_tab()
        self._build_runtime_tab()
        self._build_console_tab()

        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(10)
        body_layout.addWidget(self._tabs, 1)

        footer_frame, _footer_layout, footer_buttons = self.create_button_bar(manifest.buttons)
        self.wire_button_actions(footer_buttons, build_devtools_button_actions(self))
        body_layout.addWidget(footer_frame)

        self.add_body_widget(body, stretch=1)

        self._refresh_timer = QTimer(self)
        self._refresh_timer.setInterval(250)
        self._refresh_timer.timeout.connect(self._refresh_views)

        self._apply_theme()
        theme.changed.connect(self._apply_theme)
        self._update_header_copy(self._tabs.currentIndex())

    def _toolbar_manifest(self, panel_id: str):
        for toolbar in self._manifest.toolbars:
            if toolbar.panel_id == panel_id:
                return toolbar
        return None

    def _build_state_tab(self) -> None:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        toolbar, toolbar_layout = self.create_toolbar()

        self._state_source_combo = QComboBox()
        self._state_source_combo.currentIndexChanged.connect(self._select_state_source)
        state_toolbar_manifest = self._toolbar_manifest("state")
        if state_toolbar_manifest is not None:
            _state_actions_frame, _state_actions_layout, state_action_buttons = self.create_manifest_toolbar(
                state_toolbar_manifest
            )
            self._state_copy_all_button = state_action_buttons["copy_all"]
            self._state_capture_button = state_action_buttons["toggle_capture"]
            self._state_copy_path_button = state_action_buttons["copy_path"]
            self.wire_button_actions(
                state_action_buttons,
                build_state_toolbar_actions(
                    window=self,
                    copy_all=self._state_vm.copyAllEntries,
                    copy_path=self._state_vm.copyCapturePath,
                ),
            )
        else:
            self._state_copy_all_button = QPushButton("Copy all")
            self._state_capture_button = QPushButton("Record")
            self._state_copy_path_button = QPushButton("Copy path")
            self.wire_button_actions(
                {
                    "copy_all": self._state_copy_all_button,
                    "toggle_capture": self._state_capture_button,
                    "copy_path": self._state_copy_path_button,
                },
                build_state_toolbar_actions(
                    window=self,
                    copy_all=self._state_vm.copyAllEntries,
                    copy_path=self._state_vm.copyCapturePath,
                ),
            )

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
        self._state_tree.setUniformRowHeights(True)
        self._state_tree.setIndentation(0)
        self._state_tree.itemClicked.connect(self._handle_state_item_click)
        self._state_tree.setColumnWidth(0, 320)

        self._state_footer = self.create_footer_label()

        layout.addWidget(toolbar)
        layout.addWidget(self._state_tree, 1)
        layout.addWidget(self._state_footer)
        self._tabs.addTab(page, "State")

    def _build_runtime_tab(self) -> None:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        toolbar, toolbar_layout = self.create_toolbar()

        self._runtime_summary = QLabel("No runtime data")
        self._runtime_summary.setObjectName("SummaryLabel")
        runtime_toolbar_manifest = self._toolbar_manifest("runtime")
        if runtime_toolbar_manifest is not None:
            _runtime_actions_frame, _runtime_actions_layout, runtime_action_buttons = self.create_manifest_toolbar(
                runtime_toolbar_manifest
            )
            self._runtime_copy_button = runtime_action_buttons["copy_all"]
            self.wire_button_actions(
                runtime_action_buttons,
                build_runtime_toolbar_actions(copy_all=self._runtime_vm.copyOverview),
            )
        else:
            self._runtime_copy_button = QPushButton("Copy all")
            self.wire_button_actions(
                {"copy_all": self._runtime_copy_button},
                build_runtime_toolbar_actions(copy_all=self._runtime_vm.copyOverview),
            )

        toolbar_layout.addWidget(self._runtime_summary, 1)
        toolbar_layout.addWidget(self._runtime_copy_button)

        filters, filters_layout = self.create_compact_toolbar()

        self._runtime_filter_buttons: dict[str, QPushButton] = {}
        for state in self._runtime_vm.availableStateFilters:
            button = self.create_filter_button(state.upper())
            button.clicked.connect(
                lambda _checked=False, state_name=state: self._toggle_runtime_filter(state_name)
            )
            button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            self._runtime_filter_buttons[state] = button
            filters_layout.addWidget(button)

        filters_layout.addStretch(1)

        self._runtime_tasks = self.create_footer_label()
        self._runtime_tasks.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        self._runtime_tree = QTreeWidget()
        self._runtime_tree.setObjectName("DevToolsTree")
        self._runtime_tree.setColumnCount(7)
        self._runtime_tree.setHeaderLabels(
            ["Unit", "State", "Kind", "Execution", "Activation", "Stage", "Parent"]
        )
        self._runtime_tree.setAlternatingRowColors(True)
        self._runtime_tree.setRootIsDecorated(False)
        self._runtime_tree.setUniformRowHeights(True)
        self._runtime_tree.setIndentation(14)
        self._runtime_tree.itemClicked.connect(self._handle_runtime_item_click)
        self._runtime_tree.setColumnWidth(0, 260)
        self._runtime_tree.setColumnWidth(1, 88)
        self._runtime_tree.setColumnWidth(2, 78)
        self._runtime_tree.setColumnWidth(3, 96)
        self._runtime_tree.setColumnWidth(4, 92)
        self._runtime_tree.setColumnWidth(5, 104)
        self._runtime_tree.setColumnWidth(6, 160)

        layout.addWidget(toolbar)
        layout.addWidget(filters)
        layout.addWidget(self._runtime_tree, 1)
        layout.addWidget(self._runtime_tasks)
        self._tabs.addTab(page, "Runtime")

    def _build_console_tab(self) -> None:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        toolbar, toolbar_layout = self.create_toolbar()

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
        self._auto_scroll_check = QCheckBox("Auto-scroll")
        self._auto_scroll_check.setChecked(True)
        self._auto_scroll_check.toggled.connect(self._set_console_auto_scroll)
        console_toolbar_manifest = self._toolbar_manifest("console")
        if console_toolbar_manifest is not None:
            _console_actions_frame, _console_actions_layout, console_action_buttons = self.create_manifest_toolbar(
                console_toolbar_manifest
            )
            self._console_clear_button = console_action_buttons["clear"]
            self.wire_button_actions(
                console_action_buttons,
                build_console_toolbar_actions(window=self),
            )
        else:
            self._console_clear_button = QPushButton("Clear")
            self.wire_button_actions(
                {"clear": self._console_clear_button},
                build_console_toolbar_actions(window=self),
            )

        toolbar_layout.addWidget(self._debug_check)
        toolbar_layout.addWidget(self._info_check)
        toolbar_layout.addWidget(self._warning_check)
        toolbar_layout.addWidget(self._error_check)
        toolbar_layout.addWidget(self._auto_scroll_check)
        toolbar_layout.addStretch(1)
        toolbar_layout.addWidget(self._console_clear_button)

        category_bar, category_layout = self.create_compact_toolbar()

        self._console_all_categories_button = self.create_filter_button("ALL")
        self._console_all_categories_button.clicked.connect(self._toggle_all_console_categories)
        category_layout.addWidget(self._console_all_categories_button)

        self._console_category_container = QWidget()
        self._console_category_layout = QHBoxLayout(self._console_category_container)
        self._console_category_layout.setContentsMargins(0, 0, 0, 0)
        self._console_category_layout.setSpacing(6)
        self._console_category_buttons: dict[str, QPushButton] = {}

        category_scroll = QScrollArea()
        category_scroll.setObjectName("CategoryScrollArea")
        category_scroll.setWidgetResizable(True)
        category_scroll.setFrameShape(QFrame.Shape.NoFrame)
        category_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        category_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        category_scroll.setWidget(self._console_category_container)
        category_layout.addWidget(category_scroll, 1)

        self._console = QPlainTextEdit()
        self._console.setObjectName("ConsoleOutput")
        self._console.setReadOnly(True)

        self._console_footer = self.create_footer_label()

        layout.addWidget(toolbar)
        layout.addWidget(category_bar)
        layout.addWidget(self._console, 1)
        layout.addWidget(self._console_footer)
        self._tabs.addTab(page, "Console")

    def _apply_theme(self) -> None:
        self.setStyleSheet(
            f"""
            {self.apply_shared_chrome_styles()}
            {self.apply_shared_toolbar_styles()}
            {self.apply_shared_interactive_styles(include_checkboxes=True)}
            QTabWidget::pane {{
                border: 1px solid {self._theme.border};
                background-color: {self._theme.surface};
                top: -1px;
            }}
            QTabBar {{
                background-color: {self._theme.surfaceAlt};
            }}
            QTabBar::tab {{
                background-color: transparent;
                color: {self._theme.textSecondary};
                border: none;
                border-bottom: 2px solid transparent;
                padding: 6px 14px;
                margin-right: 0px;
                min-width: 84px;
                font-family: "Consolas";
                font-size: 11px;
            }}
            QTabBar::tab:selected {{
                background-color: transparent;
                color: {self._theme.accent};
                border-bottom: 2px solid {self._theme.accent};
            }}
            QTabBar::tab:hover:!selected {{
                background-color: {with_alpha(self._theme.accent, 0.08)};
                color: {self._theme.text};
            }}
            QLabel#SummaryLabel {{
                color: {self._theme.textSecondary};
                font-size: {self._theme.fontSizeSmall}px;
                font-family: "Consolas";
            }}
            QFrame#DevToolsToolbar {{
                border-radius: 0px;
                border-left: none;
                border-right: none;
            }}
            QTreeWidget#DevToolsTree, QPlainTextEdit#ConsoleOutput {{
                background-color: {self._theme.surface};
                border: 1px solid {self._theme.border};
                alternate-background-color: {with_alpha(self._theme.surfaceAlt, 0.32)};
            }}
            QTreeView::item {{
                min-height: 22px;
            }}
            QHeaderView::section {{
                background-color: {self._theme.surfaceAlt};
                color: {self._theme.textMuted};
                border: none;
                border-bottom: 1px solid {self._theme.border};
                padding: 4px 8px;
                font-weight: 600;
                font-family: "Consolas";
                font-size: 10px;
            }}
            QPushButton#RuntimeFilterButton {{
                min-width: 0px;
                padding: 2px 8px;
                border-radius: 3px;
                color: {self._theme.textMuted};
                font-family: "Consolas";
                font-size: 10px;
            }}
            QPushButton#RuntimeFilterButton:checked {{
                color: {self._theme.accent};
                border-color: {self._theme.accent};
                background-color: {with_alpha(self._theme.accent, 0.12)};
            }}
            QComboBox {{
                font-family: "Consolas";
                font-size: 11px;
                min-height: 24px;
            }}
            QCheckBox {{
                font-family: "Consolas";
                font-size: 10px;
            }}
            QScrollArea#CategoryScrollArea {{
                background-color: transparent;
            }}
            QPlainTextEdit#ConsoleOutput {{
                color: {self._theme.text};
                selection-background-color: {with_alpha(self._theme.accent, 0.18)};
                font-family: "Consolas";
                font-size: 11px;
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

    def _set_console_auto_scroll(self, checked: bool) -> None:
        self._console_auto_scroll = checked

    def _clear_console(self) -> None:
        self._log_inspector.clear()
        self._last_log_count = 0
        self._refresh_console_view()

    def _refresh_views(self) -> None:
        self._refresh_state_view()
        self._refresh_runtime_view()
        self._refresh_console_view()
        self._update_header_copy(self._tabs.currentIndex())

    def _update_header_copy(self, index: int) -> None:
        if index == 0:
            subtitle = "Inspect live source snapshots, collapse sections, and copy exact state values from the active source."
        elif index == 1:
            subtitle = "Follow the runtime graph, unit ownership, and execution state in the current host."
        else:
            subtitle = "Filter Python logs by severity and review recent host activity in one shared console."
        self._subtitle_label.setText(subtitle)

    def _refresh_state_toolbar(self) -> None:
        capture_active = self._state_vm.captureActive
        self._state_capture_button.setText("Recording" if capture_active else "Record")
        self._state_copy_path_button.setEnabled(capture_active)
        self._state_copy_all_button.setEnabled(bool(self._state_vm.entries))
        sources = self._state_vm.sources
        selected = self._state_vm.selectedIndex
        source_label = ""
        if 0 <= selected < len(sources):
            source_label = str(sources[selected].get("label", ""))
        entry_count = len(self._state_vm.entries)
        footer_text = []
        if source_label:
            footer_text.append(f"Source: {source_label}")
        footer_text.append(f"Entries: {entry_count}")
        if capture_active:
            footer_text.append("Capture active")
        self._state_footer.setVisible(bool(footer_text))
        self._state_footer.setText("  |  ".join(footer_text))

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
        self._state_tree.resizeColumnToContents(0)
        self._refresh_state_toolbar()

    def _refresh_runtime_view(self) -> None:
        self._runtime_summary.setText(self._runtime_vm.summary or "No runtime data")
        for state, button in self._runtime_filter_buttons.items():
            button.blockSignals(True)
            button.setChecked(state in self._runtime_vm.stateFilters)
            button.blockSignals(False)

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
                str(unit["activation"]),
                str(unit["stage"]),
                parent_id,
            ]
            item = QTreeWidgetItem(row)
            item.setData(0, Qt.ItemDataRole.UserRole, unit_id)
            item.setData(0, Qt.ItemDataRole.UserRole + 1, bool(unit.get("hasChildren", False)))
            item.setData(0, Qt.ItemDataRole.UserRole + 2, bool(unit.get("expanded", False)))
            item.setForeground(0, QColor(self._theme.text))
            item.setForeground(1, QColor(self._theme.accent if str(unit["state"]) == "running" else self._theme.textSecondary))
            item.setForeground(2, QColor(self._theme.textSecondary))
            item.setForeground(3, QColor(self._theme.textSecondary))
            item.setForeground(4, QColor(self._theme.textMuted))
            item.setForeground(5, QColor(self._theme.textMuted))
            item.setForeground(6, QColor(self._theme.textMuted))
            if parent_id and parent_id in items_by_id:
                items_by_id[parent_id].addChild(item)
            else:
                self._runtime_tree.addTopLevelItem(item)
            items_by_id[unit_id] = item
        for item in items_by_id.values():
            if bool(item.data(0, Qt.ItemDataRole.UserRole + 1)):
                item.setExpanded(bool(item.data(0, Qt.ItemDataRole.UserRole + 2)))
        self._runtime_copy_button.setEnabled(bool(self._runtime_vm.units))
        task_ids = self._runtime_vm.taskIds
        self._runtime_tasks.setVisible(bool(task_ids))
        self._runtime_tasks.setText("" if not task_ids else f"Tasks: {', '.join(task_ids)}")

    def _toggle_runtime_filter(self, state: str) -> None:
        self._runtime_vm.toggleStateFilter(state)
        self._refresh_runtime_view()

    def _handle_runtime_item_click(self, item: QTreeWidgetItem, column: int) -> None:
        if column != 0:
            return
        if not bool(item.data(0, Qt.ItemDataRole.UserRole + 1)):
            return
        unit_id = item.data(0, Qt.ItemDataRole.UserRole)
        if isinstance(unit_id, str):
            self._runtime_vm.toggleExpanded(unit_id)
            self._refresh_runtime_view()

    def _toggle_all_console_categories(self) -> None:
        target = not self._log_settings_vm.allCategoriesEnabled
        self._log_settings_vm.setDevMode(target)
        self._refresh_console_categories()
        self._refresh_console_view()

    def _toggle_console_category(self, name: str) -> None:
        categories = {
            str(item["name"]): bool(item["enabled"])
            for item in self._log_settings_vm.categories
        }
        current = categories.get(name, False)
        self._log_settings_vm.setCategoryEnabled(name, not current)
        self._refresh_console_categories()
        self._refresh_console_view()

    def _refresh_console_categories(self) -> None:
        while self._console_category_layout.count():
            item = self._console_category_layout.takeAt(0)
            if item is None:
                continue
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self._console_category_buttons.clear()

        self._console_all_categories_button.blockSignals(True)
        self._console_all_categories_button.setChecked(self._log_settings_vm.allCategoriesEnabled)
        self._console_all_categories_button.blockSignals(False)

        for category in self._log_settings_vm.categories:
            name = str(category["name"])
            enabled = bool(category["enabled"])
            button = self.create_filter_button(name)
            button.setChecked(enabled)
            button.clicked.connect(lambda _checked=False, category_name=name: self._toggle_console_category(category_name))
            self._console_category_buttons[name] = button
            self._console_category_layout.addWidget(button)
        self._console_category_layout.addStretch(1)

    def _log_visible(self, level: str) -> bool:
        if level == "DEBUG":
            return self._console_debug
        if level == "INFO":
            return self._console_info
        if level == "WARNING":
            return self._console_warning
        return self._console_error

    def _console_category_visible(self, logger_name: str) -> bool:
        categories = self._log_settings_vm.categories
        if not categories or self._log_settings_vm.allCategoriesEnabled:
            return True
        enabled_names = {
            str(item["name"])
            for item in categories
            if bool(item["enabled"])
        }
        if not enabled_names:
            return False
        return any(
            logger_name == name
            or logger_name.endswith("." + name)
            or name in logger_name
            for name in enabled_names
        )

    def _refresh_console_view(self) -> None:
        self._refresh_console_categories()
        records = [
            entry
            for entry in self._log_inspector.records()
            if self._log_visible(entry.level) and self._console_category_visible(entry.name)
        ]
        self._last_log_count = len(records)
        lines = [f"{entry.time}  {entry.level:<8}  {entry.name}  {entry.message}" for entry in records]
        self._console.setPlainText("\n".join(lines))
        if self._console_auto_scroll:
            cursor = self._console.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            self._console.setTextCursor(cursor)
        footer = [
            f"Lines: {len(records)}",
            "Auto-scroll" if self._console_auto_scroll else "Manual scroll",
        ]
        self._console_footer.setVisible(True)
        self._console_footer.setText("  |  ".join(footer))
