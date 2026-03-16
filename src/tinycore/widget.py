"""WidgetSpec — declarative overlay widget registration.

Plugins register WidgetSpecs to tell the UI what overlay widgets exist.
Specs are loaded from widgets.toml.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class WidgetSpec:
    """Declares an overlay widget that a plugin provides."""

    id: str
    title: str
    description: str = ""
    enable: bool = True


class WidgetRegistry:
    """Stores WidgetSpecs registered by plugins."""

    def __init__(self):
        self._specs: dict[str, WidgetSpec] = {}

    def register(self, spec: WidgetSpec) -> None:
        self._specs[spec.id] = spec

    def get(self, widget_id: str) -> WidgetSpec:
        return self._specs[widget_id]

    def all(self) -> list[WidgetSpec]:
        return list(self._specs.values())

    def has(self, widget_id: str) -> bool:
        return widget_id in self._specs


def load_widgets_toml(path: Path) -> list[WidgetSpec]:
    """Load widget specs from a widgets.toml file."""
    import tomllib

    with open(path, "rb") as f:
        data = tomllib.load(f)

    return [
        WidgetSpec(
            id=widget_id,
            title=widget_data.get("title", widget_id),
            description=widget_data.get("description", ""),
            enable=widget_data.get("enable", True),
        )
        for widget_id, widget_data in data.items()
    ]
