#  TinyUI
#  Copyright (C) 2026 Oost-hash
#
#  This file is part of TinyUI.
#
#  TinyUI is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  TinyUI is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#  TinyUI builds on TinyPedal by s-victor (https://github.com/s-victor/TinyPedal),
#  licensed under GPLv3.

from PySide6.QtCore import Property, QObject, QTimer, Signal, Slot
from PySide6.QtQml import QmlElement, QmlSingleton

from tinyruntime_schema import get_logger

QML_IMPORT_NAME = "TinyUI"
QML_IMPORT_MAJOR_VERSION = 1

log = get_logger(__name__)


@QmlElement
@QmlSingleton
class StatusBarViewModel(QObject):
    """Manages the state of the status bar and the plugin dropdown."""

    pluginDropdownOpenChanged = Signal()
    activePluginIndexChanged  = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._plugin_dropdown_open: bool = False
        self._active_plugin_index:  int  = 0

    # ── Properties ────────────────────────────────────────────────────────

    @Property(bool, notify=pluginDropdownOpenChanged)
    def pluginDropdownOpen(self) -> bool:
        return self._plugin_dropdown_open

    @Property(int, notify=activePluginIndexChanged)
    def activePluginIndex(self) -> int:
        return self._active_plugin_index

    # ── Slots ─────────────────────────────────────────────────────────────

    @Slot(int)
    def selectPlugin(self, index: int) -> None:
        """Select plugin and close dropdown — single action for QML."""
        log.ui("selectPlugin", index=index)
        if self._active_plugin_index != index:
            self._active_plugin_index = index
            self.activePluginIndexChanged.emit()
        self._set_open(False)

    @Slot(int)
    def setActivePlugin(self, index: int) -> None:
        log.ui("setActivePlugin", index=index)
        if self._active_plugin_index != index:
            self._active_plugin_index = index
            self.activePluginIndexChanged.emit()

    @Slot()
    def togglePluginDropdown(self):
        log.ui("togglePluginDropdown", open=self._plugin_dropdown_open)
        self._set_open(not self._plugin_dropdown_open)

    @Slot()
    def closePluginDropdown(self):
        log.ui("closePluginDropdown")
        # Defer one event cycle so a propagated click can still reach the dropdown
        # item before visible=False disables the items.
        QTimer.singleShot(0, lambda: self._set_open(False))

    # ── Intern ────────────────────────────────────────────────────────────

    def _set_open(self, val: bool) -> None:
        if self._plugin_dropdown_open != val:
            self._plugin_dropdown_open = val
            self.pluginDropdownOpenChanged.emit()
