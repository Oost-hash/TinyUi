"""tinycore — generic application engine."""

from .app import App, create_app
from .config.store import ConfigStore
from .config.loader import LoaderRegistry, read_toml, write_toml
from .editor import ColumnDef, EditorRegistry, EditorSpec, load_editors_toml
from .events.bus import EventBus
from .plugin.protocol import Plugin
from .plugin.registry import PluginRegistry
from .providers.protocol import Provider
from .providers.registry import ProviderRegistry

__all__ = [
    "App",
    "create_app",
    "ConfigStore",
    "LoaderRegistry",
    "read_toml",
    "write_toml",
    "ColumnDef",
    "EditorRegistry",
    "EditorSpec",
    "load_editors_toml",
    "EventBus",
    "Plugin",
    "PluginRegistry",
    "Provider",
    "ProviderRegistry",
]
