from PySide6.QtCore import QObject


class SettingsTabViewModel(QObject):
    def __init__(self, app_state):
        super().__init__()
        self._state = app_state
