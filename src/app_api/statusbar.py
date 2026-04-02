"""StatusbarRegistry — collects statusbar items per window, listens to runtime events."""

from __future__ import annotations

from typing import Literal

from PySide6.QtCore import QObject, Signal

from runtime_schema import EventBus, EventType, StatusbarItem


class StatusbarRegistry(QObject):
    """Collects statusbar items per window, listens to runtime events."""
    
    # Signal emitted when statusbar changes (for QML)
    statusbarChanged = Signal(str)  # window_id
    activePluginChanged = Signal(str)  # plugin_id
    
    def __init__(self, event_bus: EventBus, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._items: dict[str, list[StatusbarItem]] = {}
        self._active_plugin: str | None = None
        self._event_bus = event_bus
        self._subscribe_to_events()
    
    def _subscribe_to_events(self) -> None:
        """Subscribe to runtime events with history replay."""
        self._event_bus.on(EventType.STATUSBAR_REGISTERED, self._on_statusbar_registered, replay_history=True)
        self._event_bus.on(EventType.PLUGIN_ACTIVATED, self._on_plugin_activated)
    
    def _on_statusbar_registered(self, event) -> None:
        """Handle statusbar registration from runtime."""
        data = event.data
        window_id = data.window_id
        self.add(window_id, StatusbarItem(
            icon=data.icon,
            text=data.text,
            tooltip=data.tooltip,
            action=data.action,
            side=data.side,
            source=data.get('source', 'plugin'),
        ))
        self.statusbarChanged.emit(window_id)
    
    def _on_plugin_activated(self, event) -> None:
        """Handle plugin activation - update active plugin reference."""
        data = event.data
        plugin_id = data.plugin_id
        self.set_active_plugin(plugin_id)
    
    def add(self, window_id: str, item: StatusbarItem) -> None:
        """Add a statusbar item to a window."""
        self._items.setdefault(window_id, []).append(item)
    
    def items_for(self, window_id: str, side: Literal["left", "right"] | None = None) -> list[StatusbarItem]:
        """Get statusbar items for a window, optionally filtered by side."""
        items = list(self._items.get(window_id, []))
        if side is not None:
            items = [i for i in items if i.side == side]
        return items
    
    def set_active_plugin(self, plugin_id: str | None) -> None:
        """Set the currently active plugin."""
        self._active_plugin = plugin_id
        self.activePluginChanged.emit(plugin_id or "")
    
    def get_active_plugin(self) -> str | None:
        """Get the currently active plugin ID."""
        return self._active_plugin
    
    def to_qml(self, window_id: str, side: Literal["left", "right"]) -> list[dict]:
        """Convert items to QML-compatible format."""
        items = self.items_for(window_id, side)
        return [
            {
                "icon": item.icon,
                "text": item.text,
                "tooltip": item.tooltip,
                "action": item.action,
            }
            for item in items
        ]
