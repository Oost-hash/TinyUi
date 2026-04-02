"""TabRegistry — collects tab declarations per window, listens to runtime events."""

from __future__ import annotations

from PySide6.QtCore import QObject, Signal

from app_schema.manifest import TabDecl
from runtime_schema import EventBus, EventType


class TabRegistry(QObject):
    """Collects tab declarations per window, listens to runtime events."""
    
    # Signal emitted when tabs change (for QML)
    tabsChanged = Signal(str)  # window_id
    activePluginChanged = Signal(str)  # plugin_id
    
    def __init__(self, event_bus: EventBus, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._tabs: dict[str, list[TabDecl]] = {}  # window_id -> tabs
        self._active_plugin: str | None = None
        self._event_bus = event_bus
        self._subscribe_to_events()
    
    def _subscribe_to_events(self) -> None:
        """Subscribe to runtime events with history replay."""
        self._event_bus.on(EventType.TAB_REGISTERED, self._on_tab_registered, replay_history=True)
        self._event_bus.on(EventType.PLUGIN_ACTIVATED, self._on_plugin_activated)
    
    def _on_tab_registered(self, event) -> None:
        """Handle tab registration from runtime."""
        data = event.data
        window_id = data.window_id
        # Create TabDecl from event data
        from pathlib import Path
        tab = TabDecl(
            id=data.id,
            label=data.label,
            target=data.target,
            surface=Path(data.surface),
            plugin_id=data.plugin_id,
        )
        self.register(window_id, tab)
        self.tabsChanged.emit(window_id)
    
    def _on_plugin_activated(self, event) -> None:
        """Handle plugin activation - update active plugin reference."""
        data = event.data
        plugin_id = data.plugin_id
        self.set_active_plugin(plugin_id)
    
    def register(self, window_id: str, tab: TabDecl) -> None:
        """Register a tab for a window."""
        self._tabs.setdefault(window_id, []).append(tab)
    
    def tabs_for(self, window_id: str) -> list[TabDecl]:
        """Get all tabs for a window."""
        return list(self._tabs.get(window_id, []))
    
    def tabs_for_plugin(self, window_id: str, plugin_id: str) -> list[TabDecl]:
        """Get tabs for a specific plugin on a window."""
        return [t for t in self.tabs_for(window_id) if t.plugin_id == plugin_id]
    
    def host_tabs(self, window_id: str) -> list[TabDecl]:
        """Get host (tinyui) tabs for a window."""
        return self.tabs_for_plugin(window_id, "tinyui")
    
    def set_active_plugin(self, plugin_id: str | None) -> None:
        """Set the currently active plugin."""
        self._active_plugin = plugin_id
        self.activePluginChanged.emit(plugin_id or "")
    
    def get_active_plugin(self) -> str | None:
        """Get the currently active plugin ID."""
        return self._active_plugin
    
    def active_tab_model(self, window_id: str) -> list[dict]:
        """Get tab model for QML: host tabs + active plugin tabs."""
        tabs = self.host_tabs(window_id)
        if self._active_plugin:
            tabs = tabs + self.tabs_for_plugin(window_id, self._active_plugin)
        
        return [
            {
                "id": t.id,
                "label": t.label,
                "surface": t.surface.as_uri(),  # Use file:// URI format
                "plugin_id": t.plugin_id,
            }
            for t in tabs
        ]
