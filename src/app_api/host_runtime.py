"""Bridge between QML and Python runtime for host operations."""

from __future__ import annotations

from PySide6.QtCore import Property, QObject, Signal, Slot

from runtime_schema import EventBus, Event, EventType, PluginStateData, PluginErrorData


class HostRuntimeBridge(QObject):
    """Exposes runtime operations and UI state to QML via Qt signals."""
    
    # Signals for QML
    activePluginChanged = Signal(str)       # plugin_id
    pluginStateChanged = Signal(str, str)   # plugin_id, state_name
    pluginError = Signal(str, str)          # plugin_id, error_message
    
    # UI state signals
    menuItemsChanged = Signal()             # menu items updated
    pluginMenuItemsChanged = Signal()       # plugin menu items updated
    statusbarItemsChanged = Signal()        # statusbar items updated
    tabModelChanged = Signal()              # tab model updated
    
    def __init__(self, event_bus: EventBus, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._event_bus = event_bus
        
        # UI state (accumulated from events)
        self._menu_items: list[dict] = []
        self._plugin_menu_labels: dict[str, str] = {}  # plugin_id -> label
        self._plugin_menu_items: dict[str, list[dict]] = {}  # plugin_id -> items
        self._statusbar_left: list[dict] = []
        self._statusbar_right: list[dict] = []
        self._all_tabs: list[dict] = []  # All tabs from all plugins
        self._active_plugin: str = ""
        
        # Subscribe to events
        self._subscribe_to_events()
    
    def _subscribe_to_events(self) -> None:
        """Subscribe to runtime events with history replay.
        
        replay_history=True ensures we receive all MENU_REGISTERED, TAB_REGISTERED, 
        etc. events that were emitted before this bridge was created.
        """
        # Plugin lifecycle events
        self._event_bus.on(EventType.PLUGIN_STATE_CHANGED, self._on_state_changed)
        self._event_bus.on(EventType.PLUGIN_ERROR, self._on_error)
        self._event_bus.on(EventType.PLUGIN_ACTIVATED, self._on_plugin_activated)
        
        # UI registration events - replay history to catch events from before we existed
        self._event_bus.on(EventType.MENU_REGISTERED, self._on_menu_registered, replay_history=True)
        self._event_bus.on(EventType.STATUSBAR_REGISTERED, self._on_statusbar_registered, replay_history=True)
        self._event_bus.on(EventType.TAB_REGISTERED, self._on_tab_registered, replay_history=True)
    
    # ── Event Handlers ─────────────────────────────────────────────────────
    
    def _on_state_changed(self, event: Event[PluginStateData]) -> None:
        """Forward runtime state changes to QML."""
        data = event.data
        self.pluginStateChanged.emit(data.plugin_id, data.new_state)
    
    def _on_error(self, event: Event) -> None:
        """Forward plugin errors to QML."""
        data = event.data
        if isinstance(data, PluginErrorData):
            self.pluginError.emit(data.plugin_id, data.error_message)
    
    def _on_plugin_activated(self, event: Event) -> None:
        """Handle plugin activation - update active plugin and filter tabs/menu."""
        data = event.data
        plugin_id = data.plugin_id
        self._active_plugin = plugin_id
        self.activePluginChanged.emit(plugin_id)
        # Update tab model to show only host + active plugin tabs
        self._update_tab_model()
        # Update plugin menu to show only active plugin's menu
        self.pluginMenuItemsChanged.emit()
    
    def _on_menu_registered(self, event: Event) -> None:
        """Handle menu registration from runtime."""
        data = event.data
        
        if data.separator:
            item = {"separator": True, "label": ""}
        else:
            item = {"label": data.label, "action": data.action}
        
        # Separate host menu from plugin menus
        if data.source == "host":
            self._menu_items.append(item)
            self.menuItemsChanged.emit()
        else:
            # Plugin menu - store per plugin_id
            window_id = data.window_id
            if window_id.startswith("plugin:"):
                plugin_id = window_id.replace("plugin:", "")
                # Extract label from plugin_id (convert dumb_plugin -> Dumb Plugin)
                label = plugin_id.replace("_", " ").title()
                
                if plugin_id not in self._plugin_menu_items:
                    self._plugin_menu_labels[plugin_id] = label
                    self._plugin_menu_items[plugin_id] = []
                self._plugin_menu_items[plugin_id].append(item)
                self.pluginMenuItemsChanged.emit()
    
    def _on_statusbar_registered(self, event: Event) -> None:
        """Handle statusbar registration from runtime."""
        data = event.data
        item = {
            "icon": data.icon,
            "text": data.text,
            "tooltip": data.tooltip,
            "action": data.action,
        }
        if data.side == "left":
            self._statusbar_left.append(item)
        else:
            self._statusbar_right.append(item)
        self.statusbarItemsChanged.emit()
    
    def _on_tab_registered(self, event: Event) -> None:
        """Handle tab registration from runtime."""
        data = event.data
        # Convert Windows path to file URL correctly
        surface_path = data.surface
        if not surface_path.startswith("file://"):
            # Convert backslashes to forward slashes and add file://
            # On Windows: C:\path\file.qml -> file:///C:/path/file.qml
            surface_path = surface_path.replace("\\", "/")
            if not surface_path.startswith("/"):
                surface_path = "/" + surface_path
            surface_path = "file://" + surface_path
        tab = {
            "id": data.id,
            "label": data.label,
            "surface": surface_path,
            "plugin_id": data.plugin_id,
        }
        self._all_tabs.append(tab)
        # Update visible tab model
        self._update_tab_model()
    
    def _update_tab_model(self) -> None:
        """Emit signal to refresh tab model (property filters dynamically)."""
        self.tabModelChanged.emit()
    
    # ── Properties for QML ────────────────────────────────────────────────
    
    @Property(list, notify=menuItemsChanged)
    def menuItems(self) -> list[dict]:
        """Host menu items."""
        return self._menu_items
    
    @Property(list, notify=pluginMenuItemsChanged)
    def pluginMenuItems(self) -> list[dict]:
        """Plugin menu items for the active plugin only."""
        if self._active_plugin and self._active_plugin in self._plugin_menu_items:
            return self._plugin_menu_items[self._active_plugin]
        return []
    
    @Property(str, notify=pluginMenuItemsChanged)
    def pluginMenuLabel(self) -> str:
        """Plugin menu label for the active plugin."""
        if self._active_plugin and self._active_plugin in self._plugin_menu_labels:
            return self._plugin_menu_labels[self._active_plugin]
        return ""
    
    @Property(list, notify=statusbarItemsChanged)
    def statusbarLeftItems(self) -> list[dict]:
        """Left side statusbar items."""
        return self._statusbar_left
    
    @Property(list, notify=statusbarItemsChanged)
    def statusbarRightItems(self) -> list[dict]:
        """Right side statusbar items."""
        return self._statusbar_right
    
    @Property(list, notify=tabModelChanged)
    def tabModel(self) -> list[dict]:
        """Tab model for tab bar - shows host tabs + active plugin tabs only."""
        return [
            tab for tab in self._all_tabs
            if tab["plugin_id"] == "tinyui" or tab["plugin_id"] == self._active_plugin
        ]
    
    @Property(str, notify=activePluginChanged)
    def activePlugin(self) -> str:
        """Currently active plugin."""
        return self._active_plugin
    
    # ── Slots for QML ─────────────────────────────────────────────────────
    
    @Slot(str, result=bool)
    def setActivePlugin(self, plugin_id: str) -> bool:
        """Set the active plugin. Returns True on success.
        
        Note: This should emit PLUGIN_ACTIVATED event which updates state.
        """
        # This will be handled by runtime - emit event instead of direct call
        from runtime_schema import UIPluginSelectedData
        self._event_bus.emit_typed(
            EventType.UI_PLUGIN_SELECTED,
            UIPluginSelectedData(plugin_id=plugin_id)
        )
        return True
