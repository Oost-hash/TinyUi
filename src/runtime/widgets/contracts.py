"""Contracts for runtime-owned widget records."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class WidgetRuntimeStatus(StrEnum):
    """Observable runtime status for one projected widget."""

    IDLE = "idle"
    WAITING_FOR_GAME = "waiting_for_game"
    WAITING_FOR_CONNECTOR = "waiting_for_connector"
    READY = "ready"
    RENDERING = "rendering"
    HIDDEN = "hidden"
    ERROR = "error"


@dataclass(frozen=True)
class WidgetRuntimeRecord:
    """Projected runtime record for one overlay widget."""

    overlay_id: str
    widget_id: str
    widget_type: str
    label: str
    source: str
    status: WidgetRuntimeStatus
    connector_ids: tuple[str, ...]
    error_message: str = ""
