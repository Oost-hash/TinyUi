"""Contracts for declarative widget definitions."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WidgetDefinition:
    """Defines a widget contract that overlays can reference declaratively."""

    widget: str
    display_name: str
    description: str = ""
    required_bindings: tuple[str, ...] = ()
