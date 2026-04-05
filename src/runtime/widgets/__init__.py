"""Runtime-owned widget record projection."""

from runtime.widgets.contracts import WidgetRuntimeRecord, WidgetRuntimeStatus
from runtime.widgets.game_detection import detect_active_game_id
from runtime.widgets.poller import WidgetRuntimePoller
from runtime.widgets.projection import project_overlay_widget_records
from runtime.widgets.startup import start_runtime_widgets

__all__ = [
    "detect_active_game_id",
    "WidgetRuntimeRecord",
    "WidgetRuntimeStatus",
    "WidgetRuntimePoller",
    "project_overlay_widget_records",
    "start_runtime_widgets",
]
