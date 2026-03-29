from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QScrollArea,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from tinyqt_settings.button_actions import build_settings_button_actions
from tinyqt_settings_schema import SettingsSpec
from tinyqt_native.native_tool_window import NativeToolWindowBase
from tinyqt_settings.settings_rows import SettingEntry, build_setting_row


class NativeSettingsWindow(NativeToolWindowBase):
    """Native Qt settings window used for the separate TinyUI settings surface."""

    def __init__(self, *, core, theme, settings_view_model, manifest) -> None:
        super().__init__(
            title=manifest.title,
            eyebrow=manifest.window.eyebrow or "SETTINGS",
            subtitle=manifest.window.subtitle,
            theme=theme,
            object_name="NativeSettingsWindow",
            width=manifest.window.default_width,
            height=manifest.window.default_height,
            min_width=manifest.window.min_width,
            min_height=manifest.window.min_height,
        )
        self._core = core
        self._theme = theme
        self._settings_view_model = settings_view_model
        self._pending: dict[tuple[str, str], Any] = {}
        self._groups: list[tuple[str, list[SettingsSpec]]] = []

        self._plugin_list = QListWidget()
        self._plugin_list.setObjectName("PluginList")
        self._plugin_list.setMinimumWidth(152)
        self._plugin_list.setAlternatingRowColors(False)
        self._plugin_list.setSpacing(0)
        self._plugin_list.currentRowChanged.connect(self._render_plugin)

        self._summary_title = self._title_label
        self._summary_title.setObjectName("SummaryTitle")
        self._summary_text = QLabel("")
        self._summary_text.setObjectName("SummaryText")
        self._summary_text.setWordWrap(True)
        self._summary_layout.addWidget(self._summary_text)
        self._summary_layout.setContentsMargins(12, 10, 12, 10)
        self._summary_layout.setSpacing(3)

        self._content_container = QWidget()
        self._content_layout = QVBoxLayout(self._content_container)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(0)
        self._content_layout.addStretch(1)

        self._scroll_area = QScrollArea()
        self._scroll_area.setObjectName("ContentScrollArea")
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll_area.setWidget(self._content_container)

        footer_frame, _footer, footer_buttons = self.create_button_bar(manifest.buttons)
        self._revert_button = footer_buttons.get("revert")
        self._save_button = footer_buttons.get("save")
        self._close_button = footer_buttons.get("close")
        if self._revert_button is None or self._save_button is None or self._close_button is None:
            raise ValueError(
                "Native settings window manifest must declare revert, save, and close buttons"
            )
        self.wire_button_actions(footer_buttons, build_settings_button_actions(self))

        right_panel = QWidget()
        right_panel.setObjectName("RightPanel")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        right_layout.addWidget(self._summary_card)
        right_layout.addWidget(self._scroll_area, 1)

        right_layout.addWidget(footer_frame)

        splitter = QSplitter()
        splitter.setObjectName("SettingsSplitter")
        splitter.addWidget(self._plugin_list)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([168, 792])

        content_frame = QWidget()
        root_layout = QHBoxLayout(content_frame)
        root_layout.setContentsMargins(10, 10, 10, 10)
        root_layout.setSpacing(0)
        root_layout.addWidget(splitter)
        self.add_body_widget(content_frame, stretch=1)

        self._apply_theme()
        theme.changed.connect(self._apply_theme)

    def _apply_theme(self) -> None:
        self.setStyleSheet(
            f"""
            {self.apply_shared_chrome_styles()}
            {self.apply_shared_panel_styles()}
            {self.apply_shared_interactive_styles(include_checkboxes=True)}
            QWidget#RightPanel {{
                background-color: transparent;
            }}
            QSplitter::handle {{
                background-color: {self._theme.border};
                width: 1px;
            }}
            QLabel#SummaryTitle {{
                color: {self._theme.text};
                font-size: {self._theme.fontSizeBase}px;
                font-weight: 600;
            }}
            QLabel#SummaryText {{
                color: {self._theme.textMuted};
                font-size: {self._theme.fontSizeSmall}px;
            }}
            QLabel#SettingRowLabel {{
                color: {self._theme.text};
                font-size: {self._theme.fontSizeBase}px;
                font-weight: 500;
            }}
            QLabel#SettingRowDescription {{
                color: {self._theme.textMuted};
                font-size: {self._theme.fontSizeSmall}px;
            }}
            QListWidget#PluginList {{
                background-color: {self._theme.surfaceAlt};
                border: 1px solid {self._theme.border};
                outline: none;
                padding-top: 0px;
            }}
            QListWidget#PluginList::item {{
                padding: 8px 12px;
                margin: 0px;
                border-left: 2px solid transparent;
                color: {self._theme.textMuted};
            }}
            QListWidget#PluginList::item:hover {{
                background-color: {self._theme.surfaceRaised};
                color: {self._theme.text};
            }}
            QListWidget#PluginList::item:selected {{
                background-color: {self._theme.surface};
                border-left: 2px solid {self._theme.accent};
                color: {self._theme.text};
            }}
            QWidget#SettingRow {{
                background-color: transparent;
                border-bottom: 1px solid {self._theme.withAlpha(self._theme.border, 0.4)};
            }}
            QScrollArea#ContentScrollArea {{
                background-color: transparent;
                border: none;
            }}
            QScrollBar:vertical {{
                width: 10px;
                margin: 0px;
                background: transparent;
            }}
            QScrollBar::handle:vertical {{
                background-color: {self._theme.withAlpha(self._theme.border, 0.9)};
                min-height: 28px;
                border-radius: 4px;
            }}
            """
        )

    def open_window(self) -> None:
        self._reload_groups()
        if self._plugin_list.count() > 0 and self._plugin_list.currentRow() < 0:
            self._plugin_list.setCurrentRow(0)
        self._settings_view_model.openPanel()
        self.show()
        self.raise_()
        self.activateWindow()

    def toggle(self) -> None:
        if self.isVisible():
            self.hide()
            self._settings_view_model.closePanel()
            return
        self.open_window()

    def closeEvent(self, event) -> None:  # type: ignore[override]
        self._settings_view_model.closePanel()
        super().closeEvent(event)

    def _reload_groups(self) -> None:
        self._groups = self._core.host.persistence.settings_groups()
        current_plugin = self._plugin_list.currentItem().text() if self._plugin_list.currentItem() else None
        self._plugin_list.clear()
        current_row = 0
        for index, (plugin_name, _specs) in enumerate(self._groups):
            self._plugin_list.addItem(QListWidgetItem(plugin_name))
            if plugin_name == current_plugin:
                current_row = index
        if self._plugin_list.count() > 0:
            self._plugin_list.setCurrentRow(current_row)
        self._update_actions()

    def revert_pending_changes(self) -> None:
        self._pending.clear()
        self._render_plugin(self._plugin_list.currentRow())
        self._update_actions()

    def apply_pending_changes(self) -> None:
        touched_plugins: set[str] = set()
        for (plugin_name, key), value in self._pending.items():
            self._core.host.persistence.set_setting(plugin_name, key, value)
            touched_plugins.add(plugin_name)
        for plugin_name in touched_plugins:
            self._core.host.persistence.save_settings(plugin_name)
        self._pending.clear()
        self._reload_groups()
        self._update_actions()

    def _update_actions(self) -> None:
        dirty = bool(self._pending)
        if self._revert_button is not None:
            self._revert_button.setEnabled(dirty)
        if self._save_button is not None:
            self._save_button.setEnabled(dirty)

    def _clear_layout(self, layout: QVBoxLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            if item is None:
                continue
            widget = item.widget()
            child_layout = item.layout()
            if widget is not None:
                widget.deleteLater()
            elif child_layout is not None:
                while child_layout.count():
                    child_item = child_layout.takeAt(0)
                    if child_item is None:
                        continue
                    child_widget = child_item.widget()
                    if child_widget is not None:
                        child_widget.deleteLater()

    def _render_plugin(self, row: int) -> None:
        self._clear_layout(self._content_layout)
        if row < 0 or row >= len(self._groups):
            self._summary_title.setText("Settings")
            self._summary_text.setText("No settings are available in the current runtime.")
            self._content_layout.addStretch(1)
            return

        plugin_name, specs = self._groups[row]
        sections: dict[str, list[SettingEntry]] = {}
        section_order: list[str] = []
        for spec in specs:
            section_name = spec.section or "General"
            if section_name not in sections:
                sections[section_name] = []
                section_order.append(section_name)
            effective_value = self._pending.get(
                (plugin_name, spec.key),
                self._core.host.persistence.get_setting(plugin_name, spec.key),
            )
            sections[section_name].append(
                SettingEntry(plugin_name=plugin_name, spec=spec, value=effective_value)
            )

        self._summary_title.setText(plugin_name)
        self._summary_text.setText(
            f"{plugin_name} exposes {len(section_order)} settings section"
            f"{'' if len(section_order) == 1 else 's'}."
            " Changes stay local until you save."
        )

        for section_name in section_order:
            self._content_layout.addWidget(self._build_section(section_name, sections[section_name]))
        self._content_layout.addStretch(1)

    def _build_section(self, title: str, entries: Iterable[SettingEntry]) -> QWidget:
        section, layout = self.create_section_frame()

        title_label = QLabel(title)
        title_label.setObjectName("SectionLabel")
        layout.addWidget(title_label)

        for entry in entries:
            layout.addWidget(
                build_setting_row(
                    entry=entry,
                    theme=self._theme,
                    remember_value=self._remember_value,
                )
            )

        return section

    def _remember_value(self, plugin_name: str, key: str, value: Any) -> None:
        current = self._core.host.persistence.get_setting(plugin_name, key)
        token = (plugin_name, key)
        if value == current:
            self._pending.pop(token, None)
        else:
            self._pending[token] = value
        self._update_actions()

