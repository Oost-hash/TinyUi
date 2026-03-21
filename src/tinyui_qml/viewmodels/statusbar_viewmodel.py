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

from tinyui_qml.log import get_logger

log = get_logger(__name__)


class StatusBarViewModel(QObject):
    """Beheert de staat van de statusbalk en de plugin-dropdown."""

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
        # Defer één event-cyclus zodat een doorgepropageerde click het dropdown-item
        # nog kan bereiken voordat visible=False de items uitschakelt.
        QTimer.singleShot(0, lambda: self._set_open(False))

    # ── Intern ────────────────────────────────────────────────────────────

    def _set_open(self, val: bool) -> None:
        if self._plugin_dropdown_open != val:
            self._plugin_dropdown_open = val
            self.pluginDropdownOpenChanged.emit()
