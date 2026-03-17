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
"""EditorSpec — declarative editor registration.

Plugins register EditorSpecs to tell the UI what data editors are available.
Specs can be defined in Python or loaded from editors.toml.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Maps TOML type names to Python types
_TYPE_MAP: dict[str, type] = {
    "str": str,
    "int": int,
    "float": float,
    "bool": bool,
}


@dataclass
class ColumnDef:
    """Defines a single column in a data editor."""

    name: str
    data_type: type = str
    editable: bool = True
    width: int = 0
    default_value: Any = None
    widget: str = "default"


@dataclass
class EditorSpec:
    """Declares a data editor that a plugin wants to expose.

    Plugins create these and register them with the app.
    The UI reads them to build editor dialogs automatically.
    """

    id: str  # unique identifier, e.g. "heatmap"
    title: str  # window title, e.g. "Heatmap Editor"
    config_key: str  # key in ConfigStore (matches loader key)
    columns: list[ColumnDef]  # column definitions for the table
    has_presets: bool = True  # data is dict[preset_name, ...]
    data_field: str = ""  # if set, rows live in this field per preset
    menu: str = ""  # menu group, e.g. "Demo"
    icon: str = ""  # optional icon name


class EditorRegistry:
    """Stores EditorSpecs registered by plugins."""

    def __init__(self):
        self._specs: dict[str, EditorSpec] = {}

    def register(self, spec: EditorSpec) -> None:
        self._specs[spec.id] = spec

    def get(self, editor_id: str) -> EditorSpec:
        return self._specs[editor_id]

    def all(self) -> list[EditorSpec]:
        return list(self._specs.values())

    def has(self, editor_id: str) -> bool:
        return editor_id in self._specs


def load_editors_toml(path: Path) -> list[EditorSpec]:
    """Load editor specs from an editors.toml file.

    Example editors.toml:

        [heatmap]
        title = "Heatmap Editor"
        config = "heatmaps"
        has_presets = true
        data_field = "entries"

        [[heatmap.columns]]
        name = "temperature"
        type = "float"
        default = 0.0

        [[heatmap.columns]]
        name = "color"
        type = "str"
        default = "#FFFFFF"
    """
    import tomllib

    with open(path, "rb") as f:
        data = tomllib.load(f)

    specs = []
    for editor_id, editor_data in data.items():
        columns = []
        for col in editor_data.get("columns", []):
            columns.append(
                ColumnDef(
                    name=col["name"],
                    data_type=_TYPE_MAP.get(col.get("type", "str"), str),
                    editable=col.get("editable", True),
                    width=col.get("width", 0),
                    default_value=col.get("default"),
                    widget=col.get("widget", "default"),
                )
            )

        specs.append(
            EditorSpec(
                id=editor_id,
                title=editor_data.get("title", editor_id),
                config_key=editor_data.get("config", editor_id),
                columns=columns,
                has_presets=editor_data.get("has_presets", True),
                data_field=editor_data.get("data_field", ""),
                menu=editor_data.get("menu", ""),
                icon=editor_data.get("icon", ""),
            )
        )

    return specs
