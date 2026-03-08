"""Reusable combo box selector component."""

from PySide2.QtWidgets import QComboBox


def combo_selector(items, current, on_change=None):
    """Create a QComboBox pre-filled with items and selected value.

    items: iterable of string items.
    current: initial selected text.
    on_change: optional callback connected to currentTextChanged.
    """
    combo = QComboBox()
    combo.addItems(items)
    combo.setCurrentText(current)
    if on_change:
        combo.currentTextChanged.connect(on_change)
    return combo
