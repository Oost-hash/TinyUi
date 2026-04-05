"""Contracts for runtime-owned window records."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class WindowRuntimeStatus(StrEnum):
    """Observable runtime status for one application window."""

    IDLE = "idle"
    OPENING = "opening"
    OPEN = "open"
    HIDDEN = "hidden"
    CLOSING = "closing"
    CLOSED = "closed"
    ERROR = "error"


@dataclass(frozen=True)
class WindowRuntimeRecord:
    """Projected runtime record for one application window."""

    window_id: str
    plugin_id: str
    window_role: str
    status: WindowRuntimeStatus
    visible: bool
    surface: str
    error_message: str = ""
