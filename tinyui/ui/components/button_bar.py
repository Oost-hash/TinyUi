"""Horizontal button bar layout helper."""

from PySide2.QtWidgets import QHBoxLayout, QWidget


def button_bar(left: list[QWidget] = (), right: list[QWidget] = ()) -> QHBoxLayout:
    """Create a horizontal layout: left widgets | stretch | right widgets."""
    layout = QHBoxLayout()
    for widget in left:
        layout.addWidget(widget)
    layout.addStretch(1)
    for widget in right:
        layout.addWidget(widget)
    return layout
