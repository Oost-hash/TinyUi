"""Plugin root manifest dataclasses."""

from __future__ import annotations

from dataclasses import dataclass, field

from app_schema.connector import ConnectorManifest
from app_schema.overlay import OverlayManifest
from app_schema.ui import SettingDecl, UiManifest


@dataclass(frozen=True)
class PluginManifest:
    plugin_id: str
    plugin_type: str
    version: str
    author: str
    description: str
    icon: str
    requires: list[str]
    settings: list[SettingDecl] = field(default_factory=list)
    ui: UiManifest | None = None
    connector: ConnectorManifest | None = None
    overlay: OverlayManifest | None = None
