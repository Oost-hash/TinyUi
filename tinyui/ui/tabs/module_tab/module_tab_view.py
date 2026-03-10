# tinyui/ui/tabs/module_tab/module_tab_view.py
from PySide2.QtWidgets import QLabel, QVBoxLayout, QWidget

from .module_tab_viewmodel import ModuleTabViewModel


class ModuleTabView(QWidget):
    """
    View voor Module tab.
    """

    def __init__(self, viewmodel: ModuleTabViewModel, parent=None):
        super().__init__(parent)
        self._vm = viewmodel

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """Bouw UI"""
        layout = QVBoxLayout(self)

        # Placeholder
        label = QLabel("Module Tab - TODO")
        layout.addWidget(label)

        # TODO: Voeg module UI toe

    def _connect_signals(self):
        """Connect ViewModel signals"""
        self._vm.data_changed.connect(self._on_data_changed)

    def _on_data_changed(self):
        """Handle data changes"""
        # TODO: Update UI
        pass
