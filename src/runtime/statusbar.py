"""StatusbarRegistry — collects statusbar items per window."""

from __future__ import annotations

from typing import Literal

from runtime_schema import StatusbarItem


class StatusbarRegistry:
    """Collects statusbar items per window."""

    def __init__(self) -> None:
        self._items: dict[str, list[StatusbarItem]] = {}
        self._active_plugin: str | None = None

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
