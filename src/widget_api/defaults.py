"""Default widget definitions available to overlays."""

from __future__ import annotations

from widget_api.contracts import WidgetDefinition
from widget_api.registry import WidgetRegistry


DEFAULT_WIDGET_DEFINITIONS: tuple[WidgetDefinition, ...] = (
    WidgetDefinition(
        widget="textWidget",
        display_name="Text Widget",
        description="Displays a label with a single bound text source.",
        required_bindings=("source",),
    ),
)


def create_default_widget_registry() -> WidgetRegistry:
    """Build a registry seeded with platform default widget kinds."""

    return WidgetRegistry(DEFAULT_WIDGET_DEFINITIONS)
