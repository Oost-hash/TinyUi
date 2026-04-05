"""Widget API foundation layer."""

from widget_api.contracts import WidgetDefinition
from widget_api.defaults import DEFAULT_WIDGET_DEFINITIONS, create_default_widget_registry
from widget_api.registry import WidgetRegistry
from widget_api.runtime_host import WidgetWindowHostController, create_widget_window_host
from widget_api.window_host import WidgetWindowHost

__all__ = [
    "DEFAULT_WIDGET_DEFINITIONS",
    "WidgetDefinition",
    "WidgetRegistry",
    "WidgetWindowHostController",
    "WidgetWindowHost",
    "create_default_widget_registry",
    "create_widget_window_host",
]
