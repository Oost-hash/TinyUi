"""Runtime events - pub/sub system for state changes."""

from __future__ import annotations

from typing import Callable

StateChangeCallback = Callable[[str, str], None]  # plugin_id, state_name
ActivePluginCallback = Callable[[str], None]      # plugin_id


class EventBus:
    """Simple pub/sub event bus for runtime state changes."""
    
    def __init__(self) -> None:
        self._state_callbacks: list[StateChangeCallback] = []
        self._active_callbacks: list[ActivePluginCallback] = []
    
    def on_state_change(self, callback: StateChangeCallback) -> None:
        """Register callback for plugin state changes."""
        self._state_callbacks.append(callback)
    
    def on_active_plugin_change(self, callback: ActivePluginCallback) -> None:
        """Register callback for active plugin changes."""
        self._active_callbacks.append(callback)
    
    def emit_state_change(self, plugin_id: str, state: str) -> None:
        """Notify all state change listeners."""
        for cb in self._state_callbacks:
            cb(plugin_id, state)
    
    def emit_active_plugin_change(self, plugin_id: str) -> None:
        """Notify all active plugin listeners."""
        for cb in self._active_callbacks:
            cb(plugin_id)
