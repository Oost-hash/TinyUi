from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractSpinBox,
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from tinyui_schema import SettingsSpec


@dataclass(frozen=True)
class _SettingEntry:
    plugin_name: str
    spec: SettingsSpec
    value: Any


class NativeSettingsWindow(QWidget):
    """Native Qt settings window used for the separate TinyUI settings surface."""

    def __init__(self, *, core, theme, settings_view_model) -> None:
        super().__init__(None, Qt.WindowType.Window)
        self._core = core
        self._theme = theme
        self._settings_view_model = settings_view_model
        self._pending: dict[tuple[str, str], Any] = {}
        self._groups: list[tuple[str, list[SettingsSpec]]] = []

        self.setWindowTitle("Settings")
        self.resize(960, 620)
        self.setMinimumSize(680, 420)
        self.setObjectName("NativeSettingsWindow")

        self._plugin_list = QListWidget()
        self._plugin_list.setObjectName("PluginList")
        self._plugin_list.setMinimumWidth(190)
        self._plugin_list.setAlternatingRowColors(True)
        self._plugin_list.setSpacing(1)
        self._plugin_list.currentRowChanged.connect(self._render_plugin)

        self._eyebrow_label = QLabel("SETTINGS")
        self._eyebrow_label.setObjectName("EyebrowLabel")
        self._summary_title = QLabel("Settings")
        self._summary_title.setObjectName("SummaryTitle")
        self._summary_text = QLabel("")
        self._summary_text.setObjectName("SummaryText")
        self._summary_text.setWordWrap(True)
        self._summary_card = QFrame()
        self._summary_card.setObjectName("SummaryCard")
        self._summary_card_layout = QVBoxLayout(self._summary_card)
        self._summary_card_layout.setContentsMargins(16, 14, 16, 14)
        self._summary_card_layout.setSpacing(6)
        self._summary_card_layout.addWidget(self._eyebrow_label)
        self._summary_card_layout.addWidget(self._summary_title)
        self._summary_card_layout.addWidget(self._summary_text)

        self._content_container = QWidget()
        self._content_layout = QVBoxLayout(self._content_container)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(16)
        self._content_layout.addStretch(1)

        self._scroll_area = QScrollArea()
        self._scroll_area.setObjectName("ContentScrollArea")
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll_area.setWidget(self._content_container)

        self._revert_button = QPushButton("Revert")
        self._revert_button.setObjectName("SecondaryButton")
        self._revert_button.clicked.connect(self.revert_pending_changes)

        self._save_button = QPushButton("Save")
        self._save_button.setObjectName("PrimaryButton")
        self._save_button.clicked.connect(self.apply_pending_changes)

        self._close_button = QPushButton("Close")
        self._close_button.setObjectName("SecondaryButton")
        self._close_button.clicked.connect(self.close)

        right_panel = QWidget()
        right_panel.setObjectName("RightPanel")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(14)
        right_layout.addWidget(self._summary_card)
        right_layout.addWidget(self._scroll_area, 1)

        footer_frame = QFrame()
        footer_frame.setObjectName("FooterFrame")
        footer = QHBoxLayout()
        footer.setContentsMargins(0, 0, 0, 0)
        footer.addStretch(1)
        footer.addWidget(self._revert_button)
        footer.addWidget(self._save_button)
        footer.addWidget(self._close_button)
        footer_frame.setLayout(footer)
        right_layout.addWidget(footer_frame)

        splitter = QSplitter()
        splitter.setObjectName("SettingsSplitter")
        splitter.addWidget(self._plugin_list)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([220, 740])

        root_layout = QHBoxLayout(self)
        root_layout.setContentsMargins(18, 18, 18, 18)
        root_layout.setSpacing(0)
        root_layout.addWidget(splitter)

        self._apply_theme()
        theme.changed.connect(self._apply_theme)

    def _apply_theme(self) -> None:
        self.setStyleSheet(
            f"""
            QWidget#NativeSettingsWindow {{
                background-color: {self._theme.surface};
                color: {self._theme.text};
                font-family: "{self._theme.fontFamily}";
                font-size: {self._theme.fontSizeBase}px;
            }}
            QWidget#RightPanel {{
                background-color: transparent;
            }}
            QSplitter::handle {{
                background-color: {self._theme.border};
                width: 1px;
            }}
            QListWidget#PluginList {{
                background-color: {self._theme.surfaceAlt};
                border: 1px solid {self._theme.border};
                outline: none;
                padding-top: 10px;
            }}
            QListWidget#PluginList::item {{
                padding: 12px 14px;
                margin: 0px;
                border-left: 3px solid transparent;
                color: {self._theme.textMuted};
            }}
            QListWidget#PluginList::item:alternate {{
                background-color: {self._theme.withAlpha(self._theme.surface, 0.18)};
            }}
            QListWidget#PluginList::item:hover {{
                background-color: {self._theme.withAlpha(self._theme.accentHover, 0.10)};
                color: {self._theme.text};
            }}
            QListWidget#PluginList::item:selected {{
                background-color: {self._theme.surface};
                border-left: 3px solid {self._theme.accent};
                color: {self._theme.text};
            }}
            QLabel#EyebrowLabel {{
                color: {self._theme.accent};
                font-size: {self._theme.fontSizeSmall}px;
                font-weight: 700;
                letter-spacing: 1px;
            }}
            QFrame#SummaryCard {{
                background-color: {self._theme.surfaceAlt};
                border: 1px solid {self._theme.border};
                border-radius: 6px;
            }}
            QLabel#SummaryTitle {{
                color: {self._theme.text};
                font-size: {self._theme.fontSizeTitle}px;
                font-weight: 600;
            }}
            QLabel#SummaryText {{
                color: {self._theme.textMuted};
                font-size: {self._theme.fontSizeSmall}px;
            }}
            QLabel#SectionLabel {{
                color: {self._theme.textSecondary};
                font-size: {self._theme.fontSizeSmall}px;
                font-weight: 600;
            }}
            QFrame#SectionFrame {{
                background-color: {self._theme.surfaceAlt};
                border: 1px solid {self._theme.border};
                border-radius: 6px;
            }}
            QFrame#FooterFrame {{
                background-color: transparent;
                border-top: 1px solid {self._theme.border};
                padding-top: 10px;
            }}
            QPushButton {{
                background-color: {self._theme.surfaceFloating};
                border: 1px solid {self._theme.border};
                border-radius: 4px;
                padding: 6px 12px;
                min-width: 86px;
            }}
            QPushButton:hover {{
                background-color: {self._theme.surfaceRaised};
            }}
            QPushButton:disabled {{
                color: {self._theme.textMuted};
            }}
            QPushButton#PrimaryButton {{
                background-color: {self._theme.accent};
                border-color: {self._theme.accent};
                color: {self._theme.accentText};
                font-weight: 600;
            }}
            QPushButton#PrimaryButton:hover {{
                background-color: {self._theme.accentHover};
                border-color: {self._theme.accentHover};
            }}
            QPushButton#PrimaryButton:disabled {{
                background-color: {self._theme.surfaceRaised};
                border-color: {self._theme.border};
                color: {self._theme.textMuted};
            }}
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
                background-color: {self._theme.surfaceFloating};
                border: 1px solid {self._theme.border};
                border-radius: 4px;
                padding: 4px 8px;
                min-height: 28px;
            }}
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
                border-color: {self._theme.accent};
            }}
            QCheckBox {{
                spacing: 8px;
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
        self._revert_button.setEnabled(dirty)
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
        sections: dict[str, list[_SettingEntry]] = {}
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
            sections[section_name].append(_SettingEntry(plugin_name=plugin_name, spec=spec, value=effective_value))

        self._summary_title.setText(plugin_name)
        self._summary_text.setText(
            f"{plugin_name} exposes {len(section_order)} settings section"
            f"{'' if len(section_order) == 1 else 's'} in the current runtime."
            " Changes stay local until you save."
        )

        for section_name in section_order:
            self._content_layout.addWidget(self._build_section(section_name, sections[section_name]))
        self._content_layout.addStretch(1)

    def _build_section(self, title: str, entries: Iterable[_SettingEntry]) -> QWidget:
        section = QFrame()
        section.setObjectName("SectionFrame")
        layout = QVBoxLayout(section)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        title_label = QLabel(title)
        title_label.setObjectName("SectionLabel")
        layout.addWidget(title_label)

        for entry in entries:
            layout.addWidget(self._build_setting_row(entry))

        return section

    def _build_setting_row(self, entry: _SettingEntry) -> QWidget:
        row = QWidget()
        row.setObjectName("SettingRow")
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 6, 0, 6)
        layout.setSpacing(12)

        text_column = QVBoxLayout()
        text_column.setContentsMargins(0, 0, 0, 0)
        text_column.setSpacing(2)

        label = QLabel(entry.spec.label)
        label.setStyleSheet("font-weight: 500;")
        description = QLabel(entry.spec.description or "")
        description.setWordWrap(True)
        description.setStyleSheet(f"color: {self._theme.textMuted}; font-size: {self._theme.fontSizeSmall}px;")
        text_column.addWidget(label)
        if entry.spec.description:
            text_column.addWidget(description)

        editor = self._build_editor(entry)
        editor.setMinimumWidth(180)

        layout.addLayout(text_column, 1)
        layout.addWidget(
            editor,
            0,
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
        )
        return row

    def _remember_value(self, plugin_name: str, key: str, value: Any) -> None:
        current = self._core.host.persistence.get_setting(plugin_name, key)
        token = (plugin_name, key)
        if value == current:
            self._pending.pop(token, None)
        else:
            self._pending[token] = value
        self._update_actions()

    def _build_editor(self, entry: _SettingEntry) -> QWidget:
        spec = entry.spec
        plugin_name = entry.plugin_name
        key = spec.key

        if spec.type == "bool":
            checkbox = QCheckBox("Enabled")
            checkbox.setChecked(bool(entry.value))
            checkbox.toggled.connect(lambda checked, pn=plugin_name, setting_key=key: self._remember_value(pn, setting_key, checked))
            return checkbox

        if spec.type == "enum":
            combo = QComboBox()
            for option in spec.options or []:
                combo.addItem(str(option))
            current_text = str(entry.value)
            index = combo.findText(current_text)
            if index >= 0:
                combo.setCurrentIndex(index)
            combo.currentTextChanged.connect(lambda text, pn=plugin_name, setting_key=key: self._remember_value(pn, setting_key, text))
            return combo

        if spec.type == "int":
            spin = QSpinBox()
            spin.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
            spin.setRange(int(spec.min if spec.min is not None else -1_000_000), int(spec.max if spec.max is not None else 1_000_000))
            spin.setSingleStep(int(spec.step if spec.step is not None else 1))
            spin.setValue(int(entry.value))
            spin.valueChanged.connect(lambda value, pn=plugin_name, setting_key=key: self._remember_value(pn, setting_key, int(value)))
            return spin

        if spec.type == "float":
            spin = QDoubleSpinBox()
            spin.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
            spin.setDecimals(2)
            spin.setRange(float(spec.min if spec.min is not None else -1_000_000.0), float(spec.max if spec.max is not None else 1_000_000.0))
            spin.setSingleStep(float(spec.step if spec.step is not None else 0.1))
            spin.setValue(float(entry.value))
            spin.valueChanged.connect(lambda value, pn=plugin_name, setting_key=key: self._remember_value(pn, setting_key, float(value)))
            return spin

        if spec.type == "string":
            line_edit = QLineEdit(str(entry.value))
            line_edit.textChanged.connect(lambda text, pn=plugin_name, setting_key=key: self._remember_value(pn, setting_key, text))
            return line_edit

        fallback = QLabel(str(entry.value))
        fallback.setStyleSheet(f"color: {self._theme.textMuted};")
        return fallback
