"""Code emitters - vervangt Jinja templates.

Elke emit_* functie neemt een AST node en retourneert Python code als string.
"""

from __future__ import annotations

from ..model import Cell, Component, Field, WarningFlash, WidgetAST


def _repr(value) -> str:
    """Repr met correcte formatting voor code output."""
    return repr(value)


def _kwargs_str(d: dict) -> str:
    """Dict naar keyword arguments string."""
    return ", ".join(f"{k}={_repr(v)}" for k, v in d.items())


def _field_line(name: str, type_hint: str, default, is_mutable: bool = False) -> str:
    """Genereer een dataclass field regel."""
    if is_mutable:
        return f"    {name}: {type_hint} = field(default_factory=lambda: {_repr(default)})"
    return f"    {name}: {type_hint} = {_repr(default)}"


# ---------------------------------------------------------------------------
# Component emitter
# ---------------------------------------------------------------------------

def emit_component(comp: Component) -> str:
    """Emit een Component dataclass."""
    lines = ["@dataclass"]
    lines.append(f"class {comp.class_name}:")

    for f in comp.fields:
        lines.append(f"    {f.name}: {f.type} = {_repr(f.default)}")

    lines.append("")

    if comp.kind == "numbered":
        lines.append("    def to_flat(self, prefix: str, index: int) -> Dict[str, Any]:")
        lines.append("        return {")
        for f in comp.fields:
            lines.append(f'            f"{{prefix}}_{{index}}_{f.name}": self.{f.name},')
        lines.append("        }")
    elif comp.reverse_attrs:
        lines.append("    def to_flat(self, prefix: str) -> Dict[str, Any]:")
        lines.append("        return {")
        for f in comp.fields:
            if f.name in comp.reverse_attrs:
                lines.append(f'            f"{f.name}_{{prefix}}": self.{f.name},')
            else:
                lines.append(f'            f"{{prefix}}_{f.name}": self.{f.name},')
        lines.append("        }")
    else:
        lines.append("    def to_flat(self, prefix: str) -> Dict[str, Any]:")
        lines.append("        return {")
        lines.append('            f"{prefix}_{f.name}": getattr(self, f.name)')
        lines.append("            for f in fields(self)")
        lines.append("        }")

    return "\n".join(lines)


def emit_components_file(components: list[Component]) -> str:
    """Emit _components.py bestand."""
    lines = [
        "# Auto-generated component classes",
        "",
        "from dataclasses import dataclass, fields",
        "from typing import Any, Dict",
    ]

    for comp in components:
        lines.append("")
        lines.append("")
        lines.append(emit_component(comp))

    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Widget emitter
# ---------------------------------------------------------------------------

def emit_widget(ast: WidgetAST) -> str:
    """Emit een compleet widget bestand."""
    lines = [
        f"# Auto-generated widget",
        f"# Widget: {ast.name}",
        "",
        "from dataclasses import dataclass, field, fields",
        "from typing import Any, Dict, List, Optional",
        "",
        "from ._base import BarConfig, Cell, ColumnField, FontConfig, PositionConfig, WarningFlash, WidgetConfig",
        "from ._components import *",
    ]

    # Inline component classes
    inline_comps = [c for c in ast.components if not c.shared]
    for comp in inline_comps:
        lines.append("")
        lines.append("")
        lines.append(emit_component(comp))

    # Widget class
    lines.append("")
    lines.append("")
    lines.append("@dataclass")
    lines.append(f"class {ast.class_name}(WidgetConfig):")
    lines.append(f'    name: str = "{ast.name}"')

    # Base overrides
    if ast.base_keys:
        lines.append("    # base overrides")
        for key, value in ast.base_keys.items():
            lines.append(_field_line(key, type(value).__name__, value))

    # Font
    if ast.font_keys:
        lines.append(f"    font: FontConfig = field(default_factory=lambda: FontConfig({_kwargs_str(ast.font_keys)}))")

    # Position
    if ast.position_keys:
        lines.append(f"    position: PositionConfig = field(default_factory=lambda: PositionConfig({_kwargs_str(ast.position_keys)}))")

    # Bar
    if ast.bar_keys:
        lines.append(f"    bar: BarConfig = field(default_factory=lambda: BarConfig({_kwargs_str(ast.bar_keys)}))")

    # Cells
    if ast.cells:
        for cell in ast.cells:
            kwargs = {"id": cell.id, **cell.attrs}
            lines.append(f"    {cell.id}: Cell = field(default_factory=lambda: Cell({_kwargs_str(kwargs)}))")

    # Warning flash
    if ast.warning_flash and ast.warning_flash.attrs:
        lines.append(f"    warning_flash: WarningFlash = field(default_factory=lambda: WarningFlash({_kwargs_str(ast.warning_flash.attrs)}))")

    # Components (shared + inline instances)
    for comp in ast.components:
        if comp.kind == "numbered":
            lines.append(f"    {comp.prefix}s: Dict[int, {comp.class_name}] = field(default_factory=lambda: {{")
            for inst in comp.instances:
                if inst.attrs:
                    lines.append(f"        {inst.key}: {comp.class_name}({_kwargs_str(inst.attrs)}),")
                else:
                    lines.append(f"        {inst.key}: {comp.class_name}(),")
            lines.append("    })")
        else:
            for inst in comp.instances:
                if inst.attrs:
                    lines.append(f"    {inst.key}: {comp.class_name} = field(default_factory=lambda: {comp.class_name}({_kwargs_str(inst.attrs)}))")
                else:
                    lines.append(f"    {inst.key}: {comp.class_name} = field(default_factory=lambda: {comp.class_name}())")

    # Leftover
    for f in ast.leftover:
        is_mutable = isinstance(f.default, (dict, list))
        lines.append(_field_line(f.name, f.type, f.default, is_mutable))

    # to_flat method
    lines.append("")
    lines.append("    def to_flat(self) -> Dict[str, Any]:")
    lines.append("        result = super().to_flat()")
    lines.append('        result["name"] = self.name')

    if ast.bar_keys:
        lines.append("        result.update(self.bar.to_flat())")

    for cell in ast.cells:
        lines.append(f"        result.update(self.{cell.id}.to_flat())")

    if ast.warning_flash:
        for attr, flat_key in ast.warning_flash.key_map.items():
            lines.append(f'        result["{flat_key}"] = self.warning_flash.{attr}')

    for comp in ast.components:
        if comp.kind == "numbered":
            lines.append(f'        for idx, item in self.{comp.prefix}s.items():')
            lines.append(f'            result.update(item.to_flat("{comp.prefix}", idx))')
        else:
            for inst in comp.instances:
                lines.append(f'        result.update(self.{inst.key}.to_flat("{inst.key}"))')

    for f in ast.leftover:
        lines.append(f'        result["{f.name}"] = self.{f.name}')

    lines.append("        return result")
    lines.append("")

    return "\n".join(lines)
