"""Plugin runtime contracts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from runtime.persistence import ScopedSettings
    from runtime.providers.contracts import ProviderAccess


@dataclass
class PluginContext:
    """What a plugin receives upon activation."""

    plugin_id: str
    settings: ScopedSettings
    providers: "ProviderAccess"
