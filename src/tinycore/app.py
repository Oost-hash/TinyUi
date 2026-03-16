"""App container + create_app() factory."""

from __future__ import annotations

from pathlib import Path

from .config.store import ConfigStore
from .config.loader import LoaderRegistry
from .editor import EditorRegistry
from .events.bus import EventBus
from .plugin.registry import PluginRegistry
from .providers.registry import ProviderRegistry
from .widget import WidgetRegistry


class App:
    """Central application container — owns all registries."""

    def __init__(self, config_dir: Path):
        self.config = ConfigStore()
        self.loaders = LoaderRegistry(config_dir)
        self.editors = EditorRegistry()
        self.events = EventBus()
        self.plugins = PluginRegistry()
        self.providers = ProviderRegistry()
        self.widgets = WidgetRegistry()

    def start(self) -> None:
        """Start the application: emit events, start plugins."""
        self.events.emit("app.starting")
        self.plugins.start_all()
        self.events.emit("app.started")

    def stop(self) -> None:
        """Stop the application: emit events, stop plugins."""
        self.events.emit("app.stopping")
        self.plugins.stop_all()
        self.events.emit("app.stopped")


def create_app(config_dir: Path, *plugins) -> App:
    """Factory: create an App, add plugins, and run register phase.

    Args:
        config_dir: Root directory for all plugin config files.
                    Each plugin gets a subdirectory: config_dir/plugin_name/

    Usage:
        app = create_app(Path("data/config"), PluginA(), PluginB())
        app.loaders.load_all(app.config)
        app.start()
    """
    app = App(config_dir)
    for plugin in plugins:
        app.plugins.add(plugin)
    app.plugins.register_all(app)
    return app
