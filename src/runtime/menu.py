"""MenuRegistry — collects menu items per window."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MenuItem:
    label:  str
    action: str


@dataclass(frozen=True)
class MenuSeparator:
    pass


MenuEntry = MenuItem | MenuSeparator


class MenuRegistry:
    def __init__(self) -> None:
        self._items: dict[str, list[MenuEntry]] = {}

    def add(self, window_id: str, entry: MenuEntry) -> None:
        self._items.setdefault(window_id, []).append(entry)

    def items_for(self, window_id: str) -> list[MenuEntry]:
        return list(self._items.get(window_id, []))

    def to_qml(self, window_id: str) -> list[dict]:
        result = []
        for entry in self.items_for(window_id):
            if isinstance(entry, MenuSeparator):
                result.append({"separator": True, "label": ""})
            else:
                result.append({"label": entry.label, "action": entry.action})
        return result

    def scoped(self, window_id: str) -> "ScopedMenu":
        return ScopedMenu(self, window_id)


class ScopedMenu:
    """Menu view scoped to a specific window — plugins use this."""

    def __init__(self, registry: MenuRegistry, window_id: str) -> None:
        self._registry  = registry
        self._window_id = window_id

    def add(self, entry: MenuEntry) -> None:
        self._registry.add(self._window_id, entry)

    def separator(self) -> None:
        self._registry.add(self._window_id, MenuSeparator())
