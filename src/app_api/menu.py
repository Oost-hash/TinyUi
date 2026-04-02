"""MenuRegistry — collects menu items per window, listens to runtime events."""

from __future__ import annotations

from PySide6.QtCore import QObject, Signal

from runtime_schema import EventBus, EventType, MenuEntry, MenuItem, MenuSeparator


class MenuRegistry(QObject):
    """Collects menu items per window, listens to runtime events."""
    
    # Signal emitted when menu items change (for QML)
    menuChanged = Signal(str)  # window_id
    
    def __init__(self, event_bus: EventBus, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._items: dict[str, list[MenuEntry]] = {}
        self._event_bus = event_bus
        self._subscribe_to_events()
    
    def _subscribe_to_events(self) -> None:
        """Subscribe to runtime events with history replay.
        
        replay_history=True ensures we receive MENU_REGISTERED events that were
        emitted before this registry was created.
        """
        self._event_bus.on(EventType.MENU_REGISTERED, self._on_menu_registered, replay_history=True)
    
    def _on_menu_registered(self, event) -> None:
        """Handle menu registration from runtime."""
        data = event.data
        window_id = data.window_id
        
        # Single item registration
        if data.separator:
            self.add(window_id, MenuSeparator(source=data.source))
        else:
            self.add(window_id, MenuItem(
                label=data.label,
                action=data.action,
                source=data.source,
            ))
        self.menuChanged.emit(window_id)
    
    def add(self, window_id: str, entry: MenuEntry) -> None:
        """Register a menu entry for a window."""
        self._items.setdefault(window_id, []).append(entry)
    
    def items_for(self, window_id: str) -> list[MenuEntry]:
        """Get all menu entries for a window."""
        return list(self._items.get(window_id, []))
    
    def to_qml_host(self, window_id: str) -> list[dict]:
        """Get host menu items as QML-compatible dicts."""
        return self._to_qml([e for e in self.items_for(window_id) if e.source == "host"])
    
    def to_qml_plugins(self, window_id: str) -> list[dict]:
        """Get plugin menu items as QML-compatible dicts."""
        return self._to_qml([e for e in self.items_for(window_id) if e.source != "host"])
    
    def to_qml(self, window_id: str) -> list[dict]:
        """Get all menu items as QML-compatible dicts."""
        return self._to_qml(self.items_for(window_id))
    
    def get_plugin_menus(self) -> dict[str, list[dict]]:
        """Get all plugin menus (for the plugin menu dropdown).
        
        Returns: dict mapping menu label -> list of menu items
        """
        result: dict[str, list[dict]] = {}
        for window_id, items in self._items.items():
            if window_id.startswith("plugin:"):
                # This is a plugin menu - find the label from items
                # The label should come from the manifest's menu field
                # For now, use a default or extract from items
                menu_items = self._to_qml(items)
                if menu_items:
                    # Use first non-separator item to determine label, or default
                    result[window_id] = menu_items
        return result
    
    def _to_qml(self, entries: list[MenuEntry]) -> list[dict]:
        """Convert entries to QML format."""
        result = []
        for entry in entries:
            if isinstance(entry, MenuSeparator):
                result.append({"separator": True, "label": ""})
            else:
                result.append({"label": entry.label, "action": entry.action})
        return result
