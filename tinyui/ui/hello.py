# tinyui/ui/hello.py
from PySide2.QtWidgets import QLabel, QMainWindow, QVBoxLayout, QWidget

from tinyui.adapters import config


class HelloWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TinyUi - Hello")
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        api_name = config.api_name
        label = QLabel(f"Hallo! API = {api_name}")
        layout.addWidget(label)
