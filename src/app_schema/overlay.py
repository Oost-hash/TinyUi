"""Overlay-oriented manifest dataclasses."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class OverlayWidgetDecl:
    """Overlay widget declaration from manifest."""

    id: str
    widget: str
    label: str = ""
    bindings: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class OverlayManifest:
    """Overlay-specific manifest declarations."""

    connectors: list[str] = field(default_factory=list)
    modules: list[str] = field(default_factory=list)
    widgets: list[OverlayWidgetDecl] = field(default_factory=list)
