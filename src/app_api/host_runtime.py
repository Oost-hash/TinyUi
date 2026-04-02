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

"""Bridge between QML and Python runtime for host operations."""

from __future__ import annotations

from PySide6.QtCore import QObject, Signal, Slot


class HostRuntimeBridge(QObject):
    """Exposes runtime operations to QML."""
    
    # Signals emitted when state changes
    activePluginChanged = Signal(str)  # plugin_id
    tabModelChanged = Signal(list)  # tab_model
    
    def __init__(self, runtime: object, main_window_id: str = "") -> None:
        super().__init__()
        self._runtime = runtime
        self._main_window_id = main_window_id
    
    @Slot(str, result=bool)
    def setActivePlugin(self, plugin_id: str) -> bool:
        """Set the active plugin. Returns True on success."""
        print(f"[HostRuntimeBridge] setActivePlugin called: {plugin_id}")
        if hasattr(self._runtime, 'set_active_plugin'):
            result = self._runtime.set_active_plugin(plugin_id)
            print(f"[HostRuntimeBridge] set_active_plugin result: {result}")
            if result:
                self.activePluginChanged.emit(plugin_id)
                # Also emit updated tab model
                if hasattr(self._runtime, 'tabs'):
                    new_model = self._runtime.tabs.active_tab_model(self._main_window_id)
                    self.tabModelChanged.emit(new_model)
            return result
        return False
    
    @Slot(result=list)
    def getTabModel(self) -> list:
        """Get current tab model for main window."""
        if hasattr(self._runtime, 'tabs'):
            return self._runtime.tabs.active_tab_model(self._main_window_id)
        return []
