# tinyui/ui/tabs/module_tab/module_tab_viewmodel.py
from PySide2.QtCore import QObject, Signal


class ModuleTabViewModel(QObject):
    """
    ViewModel voor Module tab.
    """

    # Signals voor UI updates
    data_changed = Signal()

    def __init__(self):
        super().__init__()
        # TODO: Initialiseer module data

    def refresh(self):
        """Refresh module data"""
        # TODO: Laad modules
        self.data_changed.emit()
