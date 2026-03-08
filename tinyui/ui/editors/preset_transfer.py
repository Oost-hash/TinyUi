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
Preset transfer
"""

from __future__ import annotations

import logging
import re
from types import MappingProxyType

from PySide2.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
)

from tinyui.backend import regex as rxp
from tinyui.backend.formatter import format_option_name
from tinyui.backend.settings import cfg, load_setting_json_file, save_and_verify_json_file
from .._common import (
    BaseEditor,
    CompactButton,
    UIScaler,
)
from ..components.list_header import ListHeader

logger = logging.getLogger(__name__)


class PresetTransfer(BaseEditor):
    """Preset Transfer"""

    def __init__(self, parent):
        super().__init__(parent)
        self.set_utility_title("Preset Transfer")
        self.setMinimumSize(UIScaler.size(40), UIScaler.size(38))

        # Label
        self.loaded_preset = cfg.filename.setting[:-5]
        label_loaded = QLabel(f"From: <b>{self.loaded_preset}</b>")

        # Setting list
        self.listbox_setting = QListWidget(self)
        self.set_setting_list(self.listbox_setting, cfg.user.setting)

        # Preset selector
        self.dest_selector = QComboBox()
        self.dest_selector.addItems(self.set_selector_list())

        # Option type list
        self.listbox_options = QListWidget(self)
        option_types = (
            "enable_state",
            "feature_toggle",
            "update_interval",
            "position",
            "opacity",
            "layout",
            "color",
            "font",
            "prefix_and_suffix",
            "caption_text",
            "decimal_places",
            "display_order",
            "other_options",
        )
        self.set_setting_list(self.listbox_options, option_types)
        layout_dest = QHBoxLayout()
        layout_dest.addWidget(QLabel("To:"))
        layout_dest.addWidget(self.dest_selector, stretch=1)

        # Button transfer
        button_apply = CompactButton("Transfer")
        button_apply.clicked.connect(self.transfer)

        button_close = CompactButton("Close")
        button_close.clicked.connect(self.close)

        layout_button = QHBoxLayout()
        layout_button.addStretch(1)
        layout_button.addWidget(button_apply)
        layout_button.addWidget(button_close)

        # List header
        header_setting = ListHeader(self, "Setting")
        header_setting.selectAllClicked.connect(
            lambda: self._set_all_checked(self.listbox_setting, True))
        header_setting.deselectAllClicked.connect(
            lambda: self._set_all_checked(self.listbox_setting, False))

        header_options = ListHeader(self, "Option Type")
        header_options.selectAllClicked.connect(
            lambda: self._set_all_checked(self.listbox_options, True))
        header_options.deselectAllClicked.connect(
            lambda: self._set_all_checked(self.listbox_options, False))

        # Set layout
        layout_main = QGridLayout()
        layout_main.addWidget(label_loaded, 0, 0)
        layout_main.addWidget(header_setting, 1, 0)
        layout_main.addWidget(self.listbox_setting, 2, 0)
        layout_main.addLayout(layout_dest, 0, 1)
        layout_main.addWidget(header_options, 1, 1)
        layout_main.addWidget(self.listbox_options, 2, 1)
        layout_main.addLayout(layout_button, 3, 1)
        layout_main.setContentsMargins(self.MARGIN, self.MARGIN, self.MARGIN, self.MARGIN)
        self.setLayout(layout_main)

    def set_selector_list(self) -> list:
        """Set preset selector list"""
        preset_list = cfg.preset_files()
        # Remove loaded preset
        if self.loaded_preset in preset_list:
            preset_list.remove(self.loaded_preset)
        # Remove locked preset
        for name in reversed(preset_list):
            full_name = f"{name}.json"
            if full_name in cfg.user.filelock:
                preset_list.remove(name)
        return preset_list

    def set_setting_list(self, listbox: QListWidget, settings: tuple | dict):
        """Set setting list"""
        for setting_name in settings:
            item = QListWidgetItem()
            listbox.addItem(item)
            checkbox_item = QCheckBox(self)
            checkbox_item.setText(format_option_name(setting_name))
            checkbox_item.key_name = setting_name
            listbox.setItemWidget(item, checkbox_item)

    def _set_all_checked(self, listbox: QListWidget, checked: bool):
        """Set all checkboxes in a listbox"""
        for row_index in range(listbox.count()):
            listbox.itemWidget(listbox.item(row_index)).setChecked(checked)

    def get_setting_selection(self, listbox: QListWidget):
        """Get setting selection"""
        for row_index in range(listbox.count()):
            item = listbox.item(row_index)
            checkbox = listbox.itemWidget(item)
            if checkbox.isChecked():
                yield checkbox.key_name

    def transfer(self):
        """Transfer setting"""
        if not self.dest_selector.currentText():
            msg_text = "No destination preset selected or found."
            QMessageBox.warning(self, "Error", msg_text)
            return
        loaded_preset_name = f"{self.loaded_preset}.json"
        dest_preset_name = f"{self.dest_selector.currentText()}.json"
        setting_selection = tuple(self.get_setting_selection(self.listbox_setting))
        if not setting_selection:
            msg_text = "No preset setting selected.<br><br>Select at least one setting and try again."
            QMessageBox.warning(self, "Error", msg_text)
            return
        options_selection = tuple(self.get_setting_selection(self.listbox_options))
        if not options_selection:
            msg_text = "No option type selected.<br><br>Select at least one option type and try again."
            QMessageBox.warning(self, "Error", msg_text)
            return
        msg_text = (
            f"Transfer selected settings from <b>{loaded_preset_name}</b>"
            f" to <b>{dest_preset_name}</b>?<br><br>"
            "This cannot be undone!"
        )
        if not self.confirm_operation(message=msg_text):
            return
        # Load preset dict
        dest_dict = load_setting_json_file(
            filename=dest_preset_name,
            filepath=cfg.path.settings,
            dict_def=cfg.default.setting,
        )
        # Copy setting
        self.copy_setting(dest_dict, setting_selection, options_selection)
        # Save setting
        save_and_verify_json_file(
            dict_user=dest_dict,
            filename=dest_preset_name,
            filepath=cfg.path.settings,
            max_attempts=cfg.max_saving_attempts,
        )
        msg_text = (
            f"Settings are transferred from <b>{loaded_preset_name}</b>"
            f" to <b>{dest_preset_name}</b>."
        )
        QMessageBox.information(self, "Transfer Completed", msg_text)

    def copy_setting(self, dest_dict: dict, setting_selection: tuple[str, ...], options_selection: tuple[str, ...]):
        """Copy setting"""
        source_dict = MappingProxyType(cfg.user.setting)
        for setting_name, source_setting_dict in source_dict.items():
            if setting_name not in setting_selection:
                continue
            dest_setting_dict = dest_dict[setting_name]
            for option_name, option_value in source_setting_dict.items():
                if "enable" == option_name:
                    if "enable_state" in options_selection:
                        dest_setting_dict[option_name] = option_value
                    continue
                if re.search(rxp.CFG_BOOL, option_name):
                    if "feature_toggle" in options_selection:
                        dest_setting_dict[option_name] = option_value
                    continue
                if re.search("update_interval", option_name):
                    if "update_interval" in options_selection:
                        dest_setting_dict[option_name] = option_value
                    continue
                if re.search("^position_x$|^position_y$", option_name):
                    if "position" in options_selection:
                        dest_setting_dict[option_name] = option_value
                    continue
                if "opacity" == option_name:
                    if "opacity" in options_selection:
                        dest_setting_dict[option_name] = option_value
                    continue
                if "layout" == option_name:
                    if "layout" in options_selection:
                        dest_setting_dict[option_name] = option_value
                    continue
                if re.search(rxp.CFG_COLOR, option_name):
                    if "color" in options_selection:
                        dest_setting_dict[option_name] = option_value
                    continue
                if re.search("font_name|font_weight|font_size|font_offset", option_name):
                    if "font" in options_selection:
                        dest_setting_dict[option_name] = option_value
                    continue
                if re.search("prefix|suffix", option_name):
                    if "prefix_and_suffix" in options_selection:
                        dest_setting_dict[option_name] = option_value
                    continue
                if re.search("caption_text", option_name):
                    if "caption_text" in options_selection:
                        dest_setting_dict[option_name] = option_value
                    continue
                if re.search("display_order", option_name):
                    if "display_order" in options_selection:
                        dest_setting_dict[option_name] = option_value
                    continue
                if re.search("decimal_places", option_name):
                    if "decimal_places" in options_selection:
                        dest_setting_dict[option_name] = option_value
                    continue
                if "other_options" in options_selection:
                    dest_setting_dict[option_name] = option_value
                    continue


