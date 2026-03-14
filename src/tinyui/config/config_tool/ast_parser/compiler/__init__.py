"""Compiler pipeline: parser → normalize → analyze → emit."""

from .parser import parse
from .normalize import normalize
from .analyze import mark_shared_components
from .emit import emit_components_file, emit_widget

__all__ = [
    "parse",
    "normalize",
    "mark_shared_components",
    "emit_components_file",
    "emit_widget",
]
