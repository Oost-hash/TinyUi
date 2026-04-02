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
    
    # Signals for QML
    activePluginChanged = Signal(str)       # plugin_id
    pluginStateChanged = Signal(str, str)   # plugin_id, state_name
    tabModelChanged = Signal(list)          # tab_model
    
    def __init__(self, runtime: object, main_window_id: str = "") -> None:
        super().__init__()
        self._runtime = runtime
        self._main_window_id = main_window_id
        
        # Subscribe to runtime events
        if hasattr(runtime, 'events'):
            runtime.events.on_state_change(self._on_state_changed)
            runtime.events.on_active_plugin_change(self._on_active_changed)
    
    def _on_state_changed(self, plugin_id: str, state: str) -> None:
        """Forward runtime state changes to QML."""
        self.pluginStateChanged.emit(plugin_id, state)
    
    def _on_active_changed(self, plugin_id: str) -> None:
        """Forward active plugin changes to QML."""
        self.activePluginChanged.emit(plugin_id)
    
    @Slot(str, result=bool)
    def setActivePlugin(self, plugin_id: str) -> bool:
        """Set the active plugin. Returns True on success."""
        if hasattr(self._runtime, 'set_active_plugin'):
            result = self._runtime.set_active_plugin(plugin_id)
            if result and hasattr(self._runtime, 'tabs'):
                # Emit tab model update
                new_model = self._runtime.tabs.active_tab_model(self._main_window_id)
                self.tabModelChanged.emit(new_model)
            return result
        return False
    
    @Slot(str, result=str)
    def getPluginState(self, plugin_id: str) -> str:
        """Get current state of a plugin."""
        if hasattr(self._runtime, '_plugin_states'):
            sm = self._runtime._plugin_states.get(plugin_id)
            return sm.state_name if sm else "disabled"
        return "disabled"
    
    @Slot(result=list)
    def getAllPluginStates(self) -> list:
        """Get states of all plugins."""
        result = []
        if hasattr(self._runtime, '_plugin_states'):
            for pid, sm in self._runtime._plugin_states.items():
                result.append({"id": pid, "state": sm.state_name})
        return result
