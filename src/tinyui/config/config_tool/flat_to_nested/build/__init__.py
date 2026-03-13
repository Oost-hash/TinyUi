"""Bouwt gegenereerde Python code."""

from .colors import prepare as prepare_colors
from .components import prepare as prepare_components
from .setup_jinja import create
from .widgets import prepare as prepare_widget
from .writer import write_all, write_base, write_colors, write_components, write_init, write_widget

__all__ = [
    "create",
    "prepare_colors",
    "prepare_components",
    "prepare_widget",
    "write_all",
    "write_colors",
    "write_widget",
    "write_components",
    "write_base",
    "write_init",
]
