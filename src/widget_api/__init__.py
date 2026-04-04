"""Widget API foundation layer."""

from widget_api.contracts import WidgetDefinition
from widget_api.defaults import DEFAULT_WIDGET_DEFINITIONS, create_default_widget_registry
from widget_api.registry import WidgetRegistry

__all__ = [
    "DEFAULT_WIDGET_DEFINITIONS",
    "WidgetDefinition",
    "WidgetRegistry",
    "create_default_widget_registry",
]
