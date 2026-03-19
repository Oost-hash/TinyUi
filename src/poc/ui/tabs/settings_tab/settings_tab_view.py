from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class SettingsTabView(QWidget):
    def __init__(self, viewmodel):
        super().__init__()
        self._vm = viewmodel

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Settings"))

        # TODO: settings UI
