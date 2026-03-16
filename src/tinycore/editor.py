"""EditorSpec — declarative editor registration.

Plugins register EditorSpecs to tell the UI what data editors are available.
The UI reads these specs and builds the appropriate dialogs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


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

    id: str                          # unique identifier, e.g. "heatmap"
    title: str                       # window title, e.g. "Heatmap Editor"
    config_key: type                 # key in ConfigStore to read/write
    columns: list[ColumnDef]         # column definitions for the table
    has_presets: bool = True         # data is dict[preset_name, list[row]]
    icon: str = ""                   # optional icon name


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
