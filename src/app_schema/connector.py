"""Connector-oriented manifest dataclasses."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ConnectorGameDecl:
    """Connector game support declaration from manifest."""

    id: str
    detect_names: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ConnectorServiceDecl:
    """Connector service declaration from manifest."""

    module: str
    class_name: str


@dataclass(frozen=True)
class ConnectorManifest:
    """Connector-specific manifest declarations."""

    provides: list[str] = field(default_factory=list)
    games: list[ConnectorGameDecl] = field(default_factory=list)
    service: ConnectorServiceDecl | None = None
