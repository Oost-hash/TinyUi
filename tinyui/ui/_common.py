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
Shared UI primitives used across all layers.
"""

from PySide2.QtCore import QRegularExpression, Qt
from PySide2.QtGui import (
    QDoubleValidator,
    QIntValidator,
    QRegularExpressionValidator,
)
from PySide2.QtWidgets import (
    QComboBox,
    QDialog,
    QMessageBox,
    QPushButton,
)

from tinyui.backend.constants import TP_APP_NAME
from . import UIScaler

# Validator
QVAL_INTEGER = QIntValidator(-999999, 999999)
QVAL_FLOAT = QDoubleValidator(-999999.9999, 999999.9999, 6)
QVAL_COLOR = QRegularExpressionValidator(QRegularExpression('^#[0-9a-fA-F]*'))
QVAL_HEATMAP = QRegularExpressionValidator(QRegularExpression('[0-9a-zA-Z_]*'))
QVAL_FILENAME = QRegularExpressionValidator(QRegularExpression('[^\\\\/:*?"<>|]*'))


def combo_selector(items, current, on_change=None):
    """Create a QComboBox pre-filled with items and selected value.

    items: iterable of string items.
    current: initial selected text.
    on_change: optional callback connected to currentTextChanged.
    """
    combo = QComboBox()
    combo.addItems(items)
    combo.setCurrentText(current)
    if on_change:
        combo.currentTextChanged.connect(on_change)
    return combo


def singleton_dialog(dialog_type: str, show_error: bool = True):
    """Singleton dialog decorator"""

    def decorator(dialog_class: BaseDialog):

        def unset_dialog_state(pointer):
            DialogSingleton.remove(dialog_type)

        def wrapper(*args, **kwargs):
            if DialogSingleton.new(dialog_type):
                instance = dialog_class(*args, **kwargs)
                instance.destroyed.connect(unset_dialog_state)
                return instance
            return DialogSingletonError(dialog_type, show_error)

        return wrapper

    return decorator


class DialogSingleton:
    """Singleton dialog"""

    _instance_type: set[str] = set()

    def __init__(self):
        raise TypeError("not for instantiate")

    @classmethod
    def is_opened(cls, dialog_type: str) -> bool:
        """Is dialog open"""
        return dialog_type in cls._instance_type

    @classmethod
    def new(cls, dialog_type: str) -> bool:
        """Append new dialog type if not exist"""
        if dialog_type not in cls._instance_type:
            cls._instance_type.add(dialog_type)
            return True
        return False

    @classmethod
    def remove(cls, dialog_type: str):
        """Remove dialog type"""
        cls._instance_type.remove(dialog_type)


class DialogSingletonError:
    """Error dialog for singleton"""

    def __init__(self, dialog_type: str, show_error: bool = True):
        self._dialog_type = dialog_type
        self._show_error = show_error

    def _message(self, parent=None):
        """Error for qdialog"""
        if not self._show_error:
            return
        msg_text = (
            f"Already opened <b>{self._dialog_type.title()} dialog</b>."
            "<br><br>Please close previous dialog first."
        )
        QMessageBox.warning(parent, "Error", msg_text)

    def open(self, parent=None):
        self._message(parent)

    def show(self, parent=None):
        self._message(parent)

    def exec(self, parent=None):
        self._message(parent)

    def exec_(self, parent=None):
        self._message(parent)


class CompactButton(QPushButton):
    """Compact button style"""

    def __init__(self, text, parent=None, has_menu=False):
        super().__init__(text, parent)
        self.setFixedWidth(
            self.fontMetrics().boundingRect(text).width()
            + UIScaler.FONT_PIXEL_SCALED * (1 + has_menu)
        )


class BaseDialog(QDialog):
    """Base dialog class"""
    MARGIN = UIScaler.pixel(6)

    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setAttribute(Qt.WA_DeleteOnClose, True)

    def set_config_title(self, option_name: str, preset_name: str):
        """Set config dialog title"""
        self.setWindowTitle(f"{option_name} - {preset_name}")

    def set_utility_title(self, name: str):
        """Set utility dialog title"""
        self.setWindowTitle(f"{name} - {TP_APP_NAME}")

    def confirm_operation(self, title: str = "Confirm", message: str = "") -> bool:
        """Confirm operation"""
        confirm = QMessageBox.question(
            self, title, message,
            buttons=QMessageBox.Yes | QMessageBox.No,
            defaultButton=QMessageBox.No,
        )
        return confirm == QMessageBox.Yes
