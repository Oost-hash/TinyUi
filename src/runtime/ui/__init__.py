"""Runtime-owned window record projection."""

from runtime.ui.contracts import WindowRuntimeRecord, WindowRuntimeStatus
from runtime.ui.projection import project_window_records

__all__ = [
    "WindowRuntimeRecord",
    "WindowRuntimeStatus",
    "project_window_records",
]
