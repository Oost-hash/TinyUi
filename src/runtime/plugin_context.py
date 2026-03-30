"""PluginContext — what a plugin receives upon activation."""

from __future__ import annotations

from dataclasses import dataclass

from runtime.persistence import ScopedSettings


@dataclass
class PluginContext:
    plugin_id: str
    settings:  ScopedSettings
