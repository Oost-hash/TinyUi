"""Plugin runtime contracts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from runtime.persistence import ScopedSettings
    from runtime.connectors.contracts import ConnectorServiceAccess


@dataclass
class PluginContext:
    """What a plugin receives upon activation."""

    plugin_id: str
    settings: ScopedSettings
    connector_services: "ConnectorServiceAccess"
