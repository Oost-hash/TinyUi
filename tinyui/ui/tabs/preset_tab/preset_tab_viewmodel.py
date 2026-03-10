# tinyui/ui/tabs/preset_tab/preset_tab_viewmodel.py
from PySide2.QtCore import QObject, Signal


class PresetTabViewModel(QObject):
    """
    ViewModel voor Preset tab.
    """

    # Signals voor UI updates
    data_changed = Signal()

    def __init__(self):
        super().__init__()
        # TODO: Initialiseer preset data

    def refresh(self):
        """Refresh preset data"""
        # TODO: Laad presets
        self.data_changed.emit()
