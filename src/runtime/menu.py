"""MenuRegistry — collects menu items per window."""

from __future__ import annotations

from runtime_schema import MenuEntry, MenuItem, MenuSeparator


class MenuRegistry:
    """Collects menu items per window, grouped by plugin."""

    def __init__(self) -> None:
        self._items: dict[str, list[MenuEntry]] = {}

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

    def _to_qml(self, entries: list[MenuEntry]) -> list[dict]:
        """Convert entries to QML format."""
        result = []
        for entry in entries:
            if isinstance(entry, MenuSeparator):
                result.append({"separator": True, "label": ""})
            else:
                result.append({"label": entry.label, "action": entry.action})
        return result
