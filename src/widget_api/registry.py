"""Registry for known widget kinds."""

from __future__ import annotations

from widget_api.contracts import WidgetDefinition


class WidgetRegistry:
    """Stores widget definitions by widget name for overlay validation."""

    def __init__(self, definitions: tuple[WidgetDefinition, ...] = ()) -> None:
        self._definitions: dict[str, WidgetDefinition] = {}
        for definition in definitions:
            self.register(definition)

    def register(self, definition: WidgetDefinition) -> None:
        self._definitions[definition.widget] = definition

    def get(self, widget: str) -> WidgetDefinition | None:
        return self._definitions.get(widget)

    def has(self, widget: str) -> bool:
        return widget in self._definitions

    def widgets(self) -> tuple[str, ...]:
        return tuple(sorted(self._definitions))
