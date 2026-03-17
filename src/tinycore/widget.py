#  TinyUI
#  Copyright (C) 2026 Oost-hash
#
#  This file is part of TinyUI.
#
#  TinyUI is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  TinyUI is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#  TinyUI builds on TinyPedal by s-victor (https://github.com/s-victor/TinyPedal),
#  licensed under GPLv3.
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
