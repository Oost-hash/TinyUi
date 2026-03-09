# tinyui/ui/common/base_dialog.py
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QDialog, QMessageBox

from tinyui.backend.constants import TP_APP_NAME

from .scaler import UIScaler


class DialogSingleton:
    _instance_type: set[str] = set()

    def __init__(self):
        raise TypeError("not for instantiate")

    @classmethod
    def is_opened(cls, dialog_type: str) -> bool:
        return dialog_type in cls._instance_type

    @classmethod
    def new(cls, dialog_type: str) -> bool:
        if dialog_type not in cls._instance_type:
            cls._instance_type.add(dialog_type)
            return True
        return False

    @classmethod
    def remove(cls, dialog_type: str):
        cls._instance_type.remove(dialog_type)


class DialogSingletonError:
    def __init__(self, dialog_type: str, show_error: bool = True):
        self._dialog_type = dialog_type
        self._show_error = show_error

    def _message(self, parent=None):
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


def singleton_dialog(dialog_type: str, show_error: bool = True):
    """Singleton dialog decorator"""

    def decorator(dialog_class):
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


class BaseDialog(QDialog):
    """Base dialog class"""

    MARGIN = UIScaler.pixel(6)

    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setAttribute(Qt.WA_DeleteOnClose, True)

    def set_config_title(self, option_name: str, preset_name: str):
        self.setWindowTitle(f"{option_name} - {preset_name}")

    def set_utility_title(self, name: str):
        self.setWindowTitle(f"{name} - {TP_APP_NAME}")

    def confirm_operation(self, title: str = "Confirm", message: str = "") -> bool:
        confirm = QMessageBox.question(
            self,
            title,
            message,
            buttons=QMessageBox.Yes | QMessageBox.No,
            defaultButton=QMessageBox.No,
        )
        return confirm == QMessageBox.Yes
