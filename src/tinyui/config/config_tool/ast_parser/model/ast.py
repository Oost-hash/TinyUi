"""AST model - de centrale datastructuur van de config compiler.

Elke node representeert een stuk van de gegenereerde output.
De AST is het contract tussen parser en emitter.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Field:
    """Eén attribuut in een gegenereerde dataclass."""
    name: str
    type: str
    default: Any


@dataclass
class Cell:
    """Een Cell in een widget (font_color_X, bkg_color_X, etc.)."""
    id: str
    attrs: dict[str, Any] = field(default_factory=dict)


@dataclass
class Component:
    """Een herbruikbare component groep.

    Unified model voor wat voorheen numbered_auto, groupings,
    en auto_prefixes waren. Het verschil zit in `kind`.
    """
    class_name: str
    kind: str  # "numbered" | "prefixed"
    prefix: str
    fields: list[Field] = field(default_factory=list)
    defaults: dict[str, Any] = field(default_factory=dict)
    reverse_attrs: set[str] = field(default_factory=set)
    instances: list[ComponentInstance] = field(default_factory=list)
    shared: bool = False  # True = _components.py, False = inline in widget


@dataclass
class ComponentInstance:
    """Eén instance van een Component."""
    key: int | str  # index (numbered) of naam (prefixed)
    attrs: dict[str, Any] = field(default_factory=dict)


@dataclass
class WarningFlash:
    """Warning flash configuratie."""
    attrs: dict[str, Any] = field(default_factory=dict)
    key_map: dict[str, str] = field(default_factory=dict)  # attr -> originele flat key


@dataclass
class WidgetAST:
    """Volledige AST voor één widget."""
    name: str
    class_name: str = ""
    base_keys: dict[str, Any] = field(default_factory=dict)
    font_keys: dict[str, Any] = field(default_factory=dict)
    position_keys: dict[str, Any] = field(default_factory=dict)
    bar_keys: dict[str, Any] = field(default_factory=dict)
    cells: list[Cell] = field(default_factory=list)
    warning_flash: WarningFlash | None = None
    components: list[Component] = field(default_factory=list)
    leftover: list[Field] = field(default_factory=list)

    def __post_init__(self):
        if not self.class_name:
            from ..utils import to_class_name
            self.class_name = to_class_name(self.name)
