"""Tabs API for QML-facing main window tab projection."""

from __future__ import annotations

from PySide6.QtCore import Property, QObject, Signal

from runtime_schema import Event, EventBus, EventType


class TabsApi(QObject):
    """QML-facing tab model derived from runtime tab events and active plugin context."""

    tabModelChanged = Signal()

    def __init__(self, event_bus: EventBus, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._event_bus = event_bus
        self._all_tabs: list[dict] = []
        self._active_plugin: str = ""
        self._subscribe_to_events()

    def _subscribe_to_events(self) -> None:
        self._event_bus.on(EventType.TAB_REGISTERED, self._on_tab_registered, replay_history=True)
        self._event_bus.on(EventType.PLUGIN_ACTIVATED, self._on_plugin_activated)

    def _on_tab_registered(self, event: Event) -> None:
        data = event.data
        surface_path = data.surface
        if not surface_path.startswith("file://"):
            surface_path = surface_path.replace("\\", "/")
            if not surface_path.startswith("/"):
                surface_path = "/" + surface_path
            surface_path = "file://" + surface_path
        self._all_tabs.append(
            {
                "id": data.id,
                "label": data.label,
                "surface": surface_path,
                "plugin_id": data.plugin_id,
            }
        )
        self.tabModelChanged.emit()

    def _on_plugin_activated(self, event: Event) -> None:
        data = event.data
        self._active_plugin = data.plugin_id
        self.tabModelChanged.emit()

    @Property(list, notify=tabModelChanged)
    def tabModel(self) -> list[dict]:
        """Tab model for QML: host tabs plus tabs for the active plugin."""
        return [
            tab
            for tab in self._all_tabs
            if tab["plugin_id"] == "tinyui" or tab["plugin_id"] == self._active_plugin
        ]
