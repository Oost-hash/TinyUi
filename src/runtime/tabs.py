"""TabRegistry — collects tab declarations per window."""

from __future__ import annotations

from dataclasses import dataclass, field

from app_schema.manifest import TabDecl


class TabRegistry:
    """Collects tab declarations per window, grouped by plugin."""

    def __init__(self) -> None:
        self._tabs: dict[str, list[TabDecl]] = {}  # window_id -> tabs
        self._active_plugin: str | None = None

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
