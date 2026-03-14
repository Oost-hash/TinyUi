"""Normalization pass - stript default waarden uit de AST.

Werkt direct op AST nodes, geen dict-mutatie meer nodig.
"""

from __future__ import annotations

from ..model import BAR, BASE, CELL, FONT, POSITION, WARNING_FLASH, WidgetAST


def _strip_defaults(data: dict, defaults: dict) -> None:
    """Verwijder entries die gelijk zijn aan defaults. Muteert in-place."""
    for attr, default_value in defaults.items():
        if attr in data and data[attr] == default_value:
            del data[attr]


def normalize(ast: WidgetAST) -> WidgetAST:
    """Strip alle default waarden uit een WidgetAST."""

    # Bekende groepen
    _strip_defaults(ast.font_keys, FONT)
    _strip_defaults(ast.position_keys, POSITION)
    _strip_defaults(ast.bar_keys, BAR)
    _strip_defaults(ast.base_keys, BASE)

    # Cell kleuren
    for cell in ast.cells:
        _strip_defaults(cell.attrs, CELL)

    # Warning flash
    if ast.warning_flash:
        removed = []
        for attr, default_value in WARNING_FLASH.items():
            if attr in ast.warning_flash.attrs and ast.warning_flash.attrs[attr] == default_value:
                del ast.warning_flash.attrs[attr]
                removed.append(attr)
        for attr in removed:
            ast.warning_flash.key_map.pop(attr, None)

    # Component instance defaults
    for comp in ast.components:
        for inst in comp.instances:
            _strip_defaults(inst.attrs, comp.defaults)

    return ast
