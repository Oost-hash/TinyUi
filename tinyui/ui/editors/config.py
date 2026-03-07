#  TinyPedal is an open-source overlay application for racing simulation.
#  Copyright (C) 2022-2026 TinyPedal developers, see contributors.md file
#
#  This file is part of TinyPedal.
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
Config dialog
"""

from __future__ import annotations

import os
import re
import time
from typing import Callable, Mapping

from PySide2.QtCore import Qt
from PySide2.QtGui import QFontDatabase
from PySide2.QtWidgets import (
    QCompleter,
    QDialogButtonBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from tinyui.backend import regex as rxp
from tinyui.backend.constants import ConfigType
from tinyui.backend.formatter import format_option_name
from tinyui.backend.settings import cfg
from .._common import (
    QVAL_COLOR,
    QVAL_FLOAT,
    QVAL_INTEGER,
    BaseDialog,
    CompactButton,
    UIScaler,
    singleton_dialog,
)
from .._option import (
    BooleanEdit,
    ClockFormatEdit,
    ColorEdit,
    DropDownListEdit,
    FilePathEdit,
    FloatEdit,
    ImagePathEdit,
    IntegerEdit,
    StringEdit,
)
from ..dialogs import DisplayOrder

COLUMN_LABEL = 0  # grid layout column index
COLUMN_OPTION = 1


def get_font_list() -> list[str]:
    """Get all available font families list"""
    if os.getenv("PYSIDE_OVERRIDE") == "6":  # no instance in qt6
        return QFontDatabase.families()  # type: ignore[call-arg]
    return QFontDatabase().families()


# ---- Form builder helpers ----

def _build_bool(parent, value, default, **_kw):
    """Build boolean editor"""
    editor = BooleanEdit(parent)
    editor.setChecked(value)
    editor.set_default(default)
    return editor


def _build_color(parent, value, default, **_kw):
    """Build color editor"""
    editor = ColorEdit(parent, value)
    editor.setMaxLength(9)
    editor.setValidator(QVAL_COLOR)
    editor.setText(value)
    editor.set_default(default)
    return editor


def _build_path(parent, value, default, **_kw):
    """Build file path editor"""
    editor = FilePathEdit(parent, value)
    editor.setText(value)
    editor.set_default(default)
    return editor


def _build_image(parent, value, default, **_kw):
    """Build image path editor"""
    editor = ImagePathEdit(parent, value)
    editor.setText(value)
    editor.set_default(default)
    return editor


def _build_combolist(parent, value, default, items=(), **_kw):
    """Build combo droplist editor"""
    editor = DropDownListEdit(parent)
    editor.addItems(items)
    editor.setCurrentText(str(value))
    editor.set_default(default)
    return editor


def _build_clock(parent, value, default, **_kw):
    """Build clock format editor"""
    editor = ClockFormatEdit(parent)
    editor.setText(value)
    editor.set_default(default)
    return editor


def _build_string(parent, value, default, **_kw):
    """Build string editor"""
    editor = StringEdit(parent)
    editor.setText(value)
    editor.set_default(default)
    return editor


def _build_integer(parent, value, default, **_kw):
    """Build integer editor"""
    editor = IntegerEdit(parent)
    editor.setValidator(QVAL_INTEGER)
    editor.setText(str(value))
    editor.set_default(default)
    return editor


def _build_float(parent, value, default, **_kw):
    """Build float editor"""
    editor = FloatEdit(parent)
    editor.setValidator(QVAL_FLOAT)
    editor.setText(str(value))
    editor.set_default(default)
    return editor


# Dispatch table: (regex_pattern, builder_func, extra_kwargs_factory_or_None)
# Order matters — first match wins. Float is the fallthrough default.
OPTION_BUILDERS = [
    (rxp.CFG_BOOL,         _build_bool,     None),
    (rxp.CFG_COLOR,        _build_color,    None),
    (rxp.CFG_USER_PATH,    _build_path,     None),
    (rxp.CFG_USER_IMAGE,   _build_image,    None),
    (rxp.CFG_FONT_NAME,    _build_combolist, lambda: {"items": get_font_list()}),
    (rxp.CFG_HEATMAP,      _build_combolist, lambda: {"items": cfg.user.heatmap.keys()}),
    (rxp.CFG_CLOCK_FORMAT, _build_clock,    None),
    (rxp.CFG_STRING,       _build_string,   None),
    (rxp.CFG_INTEGER,      _build_integer,  None),
]


def build_option_editor(parent, key: str, value, default, option_width: int,
                        choice_dicts: tuple[Mapping, ...] = ()) -> object:
    """Build the appropriate editor widget for a config key.

    Checks choice dicts first (CHOICE_UNITS, CHOICE_COMMON), then the
    OPTION_BUILDERS dispatch table, falling back to float editor.
    """
    # Check choice dictionaries first
    for choice_dict in choice_dicts:
        for ref_key, choice_list in choice_dict.items():
            if re.search(ref_key, key):
                editor = _build_combolist(parent, value, default, items=choice_list)
                editor.setFixedWidth(option_width)
                return editor

    # Dispatch table
    for pattern, builder, extra_factory in OPTION_BUILDERS:
        if re.search(pattern, key):
            extra = extra_factory() if extra_factory else {}
            editor = builder(parent, value, default, **extra)
            editor.setFixedWidth(option_width)
            return editor

    # Fallback: float
    editor = _build_float(parent, value, default)
    editor.setFixedWidth(option_width)
    return editor


@singleton_dialog(ConfigType.CONFIG)
class FontConfig(BaseDialog):
    """Config global font setting"""

    def __init__(self, parent, user_setting: dict, reload_func: Callable):
        super().__init__(parent)
        self.set_config_title("Global Font Override", cfg.filename.setting)

        self.reloading = reload_func
        self.user_setting = user_setting

        # Create options
        self.edit_fontname = DropDownListEdit(self)
        self.edit_fontname.addItem("no change")
        self.edit_fontname.addItems(get_font_list())
        self.edit_fontname.setFixedWidth(UIScaler.size(9))

        self.edit_fontsize = QSpinBox(self)
        self.edit_fontsize.setRange(-999, 999)
        self.edit_fontsize.setFixedWidth(UIScaler.size(9))

        self.edit_fontweight = DropDownListEdit(self)
        self.edit_fontweight.addItem("no change")
        self.edit_fontweight.addItems(rxp.CHOICE_COMMON[rxp.CFG_FONT_WEIGHT])
        self.edit_fontweight.setFixedWidth(UIScaler.size(9))

        self.edit_autooffset = DropDownListEdit(self)
        self.edit_autooffset.addItems(("no change", "enable", "disable"))
        self.edit_autooffset.setFixedWidth(UIScaler.size(9))

        self.edit_fontoffset = QSpinBox(self)
        self.edit_fontoffset.setRange(-999, 999)
        self.edit_fontoffset.setFixedWidth(UIScaler.size(9))

        layout_option = QGridLayout()
        layout_option.setAlignment(Qt.AlignTop)
        layout_option.addWidget(QLabel("Font Name"), 0, 0)
        layout_option.addWidget(self.edit_fontname, 0, 1)
        layout_option.addWidget(QLabel("Font Size Addend"), 1, 0)
        layout_option.addWidget(self.edit_fontsize, 1, 1)
        layout_option.addWidget(QLabel("Font Weight"), 2, 0)
        layout_option.addWidget(self.edit_fontweight, 2, 1)
        layout_option.addWidget(QLabel("Enable Auto Font Offset"), 3, 0)
        layout_option.addWidget(self.edit_autooffset, 3, 1)
        layout_option.addWidget(QLabel("Font Offset Vertical Addend"), 4, 0)
        layout_option.addWidget(self.edit_fontoffset, 4, 1)

        # Button
        button_apply = QDialogButtonBox(QDialogButtonBox.Apply)
        button_apply.clicked.connect(self.applying)

        button_save = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_save.accepted.connect(self.saving)
        button_save.rejected.connect(self.reject)

        layout_button = QHBoxLayout()
        layout_button.addStretch(1)
        layout_button.addWidget(button_apply)
        layout_button.addWidget(button_save)

        # Set layout
        layout_main = QVBoxLayout()
        layout_main.addLayout(layout_option)
        layout_main.addLayout(layout_button)
        layout_main.setContentsMargins(self.MARGIN, self.MARGIN, self.MARGIN, self.MARGIN)
        self.setLayout(layout_main)

    def applying(self):
        """Save & apply"""
        self.save_setting(self.user_setting)

    def saving(self):
        """Save & close"""
        self.applying()
        self.accept()  # close

    def save_setting(self, dict_user: dict[str, dict]):
        """Save setting"""
        for setting in dict_user.values():
            for key in setting:
                # Font name
                if re.search(rxp.CFG_FONT_NAME, key):
                    font_name = self.edit_fontname.currentText()
                    if font_name != "no change":
                        setting[key] = font_name
                    continue
                # Font weight
                if re.search(rxp.CFG_FONT_WEIGHT, key):
                    font_weight = self.edit_fontweight.currentText()
                    if font_weight != "no change":
                        setting[key] = font_weight
                    continue
                # Font size addend
                if re.search("font_size", key):
                    font_size = self.edit_fontsize.value()
                    if font_size != 0:
                        setting[key] = max(setting[key] + font_size, 1)
                    continue
                # Auto font offset
                if key == "enable_auto_font_offset":
                    auto_offset = self.edit_autooffset.currentText()
                    if auto_offset == "disable":
                        setting[key] = False
                    elif auto_offset == "enable":
                        setting[key] = True
                    continue
                # Font offset vertical
                if key == "font_offset_vertical":
                    font_offset = self.edit_fontoffset.value()
                    if font_offset != 0:
                        setting[key] += font_offset
                    continue
        # Reset after applied
        self.edit_fontsize.setValue(0)
        self.edit_fontoffset.setValue(0)
        # Wait saving finish
        cfg.save(0)
        while cfg.is_saving:
            time.sleep(0.01)
        self.reloading()


@singleton_dialog(ConfigType.CONFIG)
class UserConfig(BaseDialog):
    """User configuration"""

    def __init__(
        self, parent, key_name: str, cfg_type: str, user_setting: dict,
        default_setting: dict, reload_func: Callable, option_width: int = 9):
        """
        Args:
            key_name: config key name.
            cfg_type: config type name from "ConfigType".
            user_setting: user setting dictionary, ex. cfg.user.setting.
            default_setting: default setting dictionary, ex. cfg.default.setting.
            reload_func: config reload (callback) function.
            option_width: option column width in pixels.
        """
        super().__init__(parent)
        self.set_config_title(format_option_name(key_name), set_preset_name(cfg_type))

        self.reloading = reload_func
        self.key_name = key_name
        self.cfg_type = cfg_type
        self.user_setting = user_setting
        self.default_setting = default_setting
        self.option_width = UIScaler.size(option_width)

        # Option dict (key: option editor)
        self.option_edit: dict = {}

        # Create options
        self.layout_option = QGridLayout()
        self.layout_option.setAlignment(Qt.AlignTop)
        option_word_set = self.create_options(self.layout_option)
        option_box = QWidget(self)
        option_box.setLayout(self.layout_option)

        # Create scroll box
        scroll_box = QScrollArea(self)
        scroll_box.setWidget(option_box)
        scroll_box.setWidgetResizable(True)

        # Search box
        auto_complete_search = QCompleter(option_word_set, self)
        auto_complete_search.setCaseSensitivity(Qt.CaseInsensitive)

        edit_search = QLineEdit(self)
        edit_search.setPlaceholderText(" Type here to search options")
        edit_search.setCompleter(auto_complete_search)
        edit_search.textChanged.connect(self.search_options)

        button_clearsearch = CompactButton("Clear")
        button_clearsearch.clicked.connect(edit_search.clear)

        layout_search = QHBoxLayout()
        layout_search.addWidget(edit_search, stretch=1)
        layout_search.addWidget(button_clearsearch)

        # Button
        has_display_order = (cfg_type == ConfigType.WIDGET and "Display" in option_word_set)
        if has_display_order:
            button_display_order = QPushButton("Configure Display Order")
            button_display_order.clicked.connect(self.open_display_order)

        button_reset = QDialogButtonBox(QDialogButtonBox.Reset)
        button_reset.clicked.connect(self.reset_setting)

        button_apply = QDialogButtonBox(QDialogButtonBox.Apply)
        button_apply.clicked.connect(self.applying)

        button_save = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_save.accepted.connect(self.saving)
        button_save.rejected.connect(self.reject)

        layout_button = QHBoxLayout()
        layout_button.addWidget(button_reset)
        layout_button.addStretch(1)
        layout_button.addWidget(button_apply)
        layout_button.addWidget(button_save)

        # Set layout
        layout_main = QVBoxLayout()
        layout_main.addLayout(layout_search)
        layout_main.addWidget(scroll_box)
        if has_display_order:
            layout_main.addWidget(button_display_order)
        layout_main.addLayout(layout_button)
        layout_main.setContentsMargins(self.MARGIN, self.MARGIN, self.MARGIN, self.MARGIN)
        self.setLayout(layout_main)
        self.setMinimumWidth(self.sizeHint().width() + UIScaler.size(2))

    def search_options(self, text: str):
        """Search for options"""
        text = text.strip().lower()
        layout_option = self.layout_option
        for row_index in range(layout_option.rowCount()):
            label = layout_option.itemAtPosition(row_index, 0).widget()
            option = layout_option.itemAtPosition(row_index, 1).widget()
            hidden = text not in label.text().lower()
            label.setHidden(hidden)
            option.setHidden(hidden)

    def open_display_order(self):
        """Open display order dialog"""
        # Extract column index setting
        user_orders = {k: v for k, v in self.user_setting[self.key_name].items() if k.startswith("display_order_")}
        default_orders = {k: v for k, v in self.default_setting[self.key_name].items() if k.startswith("display_order_")}
        dialog = DisplayOrder(self, user_orders=user_orders, default_orders=default_orders)
        dialog.open()

    def update_display_order(self, new_orders: dict):
        """Update display order index to user setting & editor"""
        self.user_setting[self.key_name].update(new_orders)
        for key, value in new_orders.items():
            if key in self.option_edit:
                self.option_edit[key].setText(str(value))

    def applying(self):
        """Save & apply"""
        self.save_setting(close=False)

    def saving(self):
        """Save & close"""
        self.save_setting(close=True)

    def reset_setting(self):
        """Reset setting"""
        msg_text = (
            f"Reset all <b>{format_option_name(self.key_name)}</b> options to default?<br><br>"
            "Changes are only saved after clicking Apply or Save Button."
        )
        if self.confirm_operation(title="Reset Options", message=msg_text):
            for editor in self.option_edit.values():
                editor.reset_to_default()

    def save_setting(self, close: bool):
        """Save setting"""
        user_setting = self.user_setting[self.key_name]
        for key, editor in self.option_edit.items():
            value = editor.validate()
            if value is None:  # abort if error found
                self.value_error_message(key)
                return
            user_setting[key] = value
        # Save global settings
        if self.cfg_type == ConfigType.CONFIG:
            cfg.update_path()
            cfg.save(0, cfg_type=ConfigType.CONFIG)
        # Save user preset settings
        else:
            cfg.save(0)
        # Wait saving finish
        while cfg.is_saving:
            time.sleep(0.01)
        # Reload
        self.reloading()
        # Close
        if close:
            self.accept()

    def value_error_message(self, option_name: str):
        """Value error message"""
        msg_text = (
            f"Invalid value for <b>{format_option_name(option_name)}</b> option."
            "<br><br>Changes are not saved."
        )
        QMessageBox.warning(self, "Error", msg_text)

    def create_options(self, layout: QGridLayout) -> set[str]:
        """Create options using the form builder"""
        option_word_set = set()
        user_data = self.user_setting[self.key_name]
        default_data = self.default_setting[self.key_name]

        for row_index, key in enumerate(user_data):
            option_name = format_option_name(key)
            option_word_set.update(option_name.split())

            # Label
            label = QLabel(option_name)
            label.setMinimumHeight(UIScaler.size(1.8))
            layout.addWidget(label, row_index, COLUMN_LABEL)

            # Editor
            editor = build_option_editor(
                parent=self,
                key=key,
                value=user_data[key],
                default=default_data[key],
                option_width=self.option_width,
                choice_dicts=(rxp.CHOICE_UNITS, rxp.CHOICE_COMMON),
            )
            layout.addWidget(editor, row_index, COLUMN_OPTION)
            self.option_edit[key] = editor

        return option_word_set


def set_preset_name(cfg_type: str) -> str:
    """Set preset name"""
    if cfg_type == ConfigType.CONFIG:
        return f"{cfg.filename.config} (global)"
    return cfg.filename.setting
