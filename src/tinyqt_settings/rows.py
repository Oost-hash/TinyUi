from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractSpinBox,
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from tinyqt_settings_schema import SettingsSpec


@dataclass(frozen=True)
class SettingEntry:
    plugin_name: str
    spec: SettingsSpec
    value: Any


def build_setting_row(
    *,
    entry: SettingEntry,
    theme,
    remember_value: Callable[[str, str, Any], None],
) -> QWidget:
    row = QWidget()
    row.setObjectName("SettingRow")
    layout = QHBoxLayout(row)
    layout.setContentsMargins(0, 2, 0, 2)
    layout.setSpacing(8)

    text_column = QVBoxLayout()
    text_column.setContentsMargins(0, 0, 0, 0)
    text_column.setSpacing(2)

    label = QLabel(entry.spec.label)
    label.setObjectName("SettingRowLabel")
    description = QLabel(entry.spec.description or "")
    description.setWordWrap(True)
    description.setObjectName("SettingRowDescription")
    text_column.addWidget(label)
    if entry.spec.description:
        text_column.addWidget(description)

    editor = build_setting_editor(
        entry=entry,
        theme=theme,
        remember_value=remember_value,
    )
    editor.setMinimumWidth(156)

    layout.addLayout(text_column, 1)
    layout.addWidget(
        editor,
        0,
        Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
    )
    return row


def build_setting_editor(
    *,
    entry: SettingEntry,
    theme,
    remember_value: Callable[[str, str, Any], None],
) -> QWidget:
    spec = entry.spec
    plugin_name = entry.plugin_name
    key = spec.key

    if spec.type == "bool":
        checkbox = QCheckBox("Enabled")
        checkbox.setChecked(bool(entry.value))
        checkbox.toggled.connect(
            lambda checked, pn=plugin_name, setting_key=key: remember_value(
                pn, setting_key, checked
            )
        )
        return checkbox

    if spec.type == "enum":
        combo = QComboBox()
        for option in spec.options or []:
            combo.addItem(str(option))
        current_text = str(entry.value)
        index = combo.findText(current_text)
        if index >= 0:
            combo.setCurrentIndex(index)
        combo.currentTextChanged.connect(
            lambda text, pn=plugin_name, setting_key=key: remember_value(
                pn, setting_key, text
            )
        )
        return combo

    if spec.type == "int":
        spin = QSpinBox()
        spin.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        spin.setRange(
            int(spec.min if spec.min is not None else -1_000_000),
            int(spec.max if spec.max is not None else 1_000_000),
        )
        spin.setSingleStep(int(spec.step if spec.step is not None else 1))
        spin.setValue(int(entry.value))
        spin.valueChanged.connect(
            lambda value, pn=plugin_name, setting_key=key: remember_value(
                pn, setting_key, int(value)
            )
        )
        return spin

    if spec.type == "float":
        spin = QDoubleSpinBox()
        spin.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        spin.setDecimals(2)
        spin.setRange(
            float(spec.min if spec.min is not None else -1_000_000.0),
            float(spec.max if spec.max is not None else 1_000_000.0),
        )
        spin.setSingleStep(float(spec.step if spec.step is not None else 0.1))
        spin.setValue(float(entry.value))
        spin.valueChanged.connect(
            lambda value, pn=plugin_name, setting_key=key: remember_value(
                pn, setting_key, float(value)
            )
        )
        return spin

    if spec.type == "string":
        line_edit = QLineEdit(str(entry.value))
        line_edit.textChanged.connect(
            lambda text, pn=plugin_name, setting_key=key: remember_value(
                pn, setting_key, text
            )
        )
        return line_edit

    fallback = QLabel(str(entry.value))
    fallback.setStyleSheet(f"color: {theme.textMuted};")
    return fallback

