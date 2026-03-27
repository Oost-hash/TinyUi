"""Optional diagnostics UI package for TinyUi development tooling."""

from .host import attach_runtime, attach_ui
from .runtime_viewmodel import RuntimeViewModel

__all__ = [
    "RuntimeViewModel",
    "attach_runtime",
    "attach_ui",
]
