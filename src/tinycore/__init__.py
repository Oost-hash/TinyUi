"""tinycore — generic application engine."""

from .app import App, create_app
from .config.store import ConfigStore
from .config.loader import ConfigLoader, LoaderRegistry, read_json, write_json
from .editor import ColumnDef, EditorRegistry, EditorSpec
from .events.bus import EventBus
from .plugin.protocol import Plugin
from .plugin.registry import PluginRegistry
from .providers.protocol import Provider
from .providers.registry import ProviderRegistry

__all__ = [
    "App",
    "create_app",
    "ConfigStore",
    "ConfigLoader",
    "LoaderRegistry",
    "read_json",
    "write_json",
    "ColumnDef",
    "EditorRegistry",
    "EditorSpec",
    "EventBus",
    "Plugin",
    "PluginRegistry",
    "Provider",
    "ProviderRegistry",
]
