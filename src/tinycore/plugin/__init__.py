"""tinycore.plugin — plugin protocol and registry."""

from .protocol import Plugin
from .registry import PluginRegistry

__all__ = ["Plugin", "PluginRegistry"]
