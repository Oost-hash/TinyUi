"""Bridge between QML and Python runtime for host operations."""

from __future__ import annotations

from PySide6.QtCore import QObject, Signal, Slot

from runtime_schema import Event, EventType, PluginStateData, PluginErrorData


class HostRuntimeBridge(QObject):
    """Exposes runtime operations to QML."""
    
    # Signals for QML
    activePluginChanged = Signal(str)       # plugin_id
    pluginStateChanged = Signal(str, str)   # plugin_id, state_name
    pluginError = Signal(str, str)          # plugin_id, error_message
    tabModelChanged = Signal(list)          # tab_model
    
    def __init__(self, runtime: object, main_window_id: str = "") -> None:
        super().__init__()
        self._runtime = runtime
        self._main_window_id = main_window_id
        
        # Subscribe to runtime events
        if hasattr(runtime, 'events'):
            runtime.events.on(EventType.PLUGIN_STATE_CHANGED, self._on_state_changed)
            runtime.events.on(EventType.PLUGIN_ERROR, self._on_error)
    
    def _on_state_changed(self, event: Event[PluginStateData]) -> None:
        """Forward runtime state changes to QML."""
        data = event.data
        self.pluginStateChanged.emit(data.plugin_id, data.new_state)
    
    def _on_error(self, event: Event) -> None:
        """Forward plugin errors to QML."""
        data = event.data
        if isinstance(data, PluginErrorData):
            self.pluginError.emit(data.plugin_id, data.error_message)
    
    @Slot(str, result=bool)
    def setActivePlugin(self, plugin_id: str) -> bool:
        """Set the active plugin. Returns True on success."""
        if hasattr(self._runtime, 'set_active_plugin'):
            result = self._runtime.set_active_plugin(plugin_id)
            if result and hasattr(self._runtime, 'tabs'):
                new_model = self._runtime.tabs.active_tab_model(self._main_window_id)
                self.tabModelChanged.emit(new_model)
            return result
        return False
    
    @Slot(str, result=str)
    def getPluginState(self, plugin_id: str) -> str:
        """Get current state of a plugin."""
        if hasattr(self._runtime, '_plugin_states'):
            from runtime.plugin_state import PluginStateMachine
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
