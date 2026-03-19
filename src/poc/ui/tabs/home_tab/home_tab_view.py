from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class HomeTabView(QWidget):
    def __init__(self, viewmodel):
        super().__init__()
        self._vm = viewmodel

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Home"))

        # TODO: echte content
