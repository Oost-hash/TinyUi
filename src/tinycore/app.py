"""App container + create_app() factory."""

from __future__ import annotations

from .config.store import ConfigStore
from .config.loader import LoaderRegistry
from .events.bus import EventBus
from .plugin.registry import PluginRegistry
from .providers.registry import ProviderRegistry


class App:
    """Central application container — owns all registries."""

    def __init__(self):
        self.config = ConfigStore()
        self.loaders = LoaderRegistry()
        self.events = EventBus()
        self.plugins = PluginRegistry()
        self.providers = ProviderRegistry()

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


def create_app(*plugins) -> App:
    """Factory: create an App, add plugins, and run register phase.

    Usage:
        app = create_app(PluginA(), PluginB())
        app.loaders.load_all(app.config)
        app.start()
    """
    app = App()
    for plugin in plugins:
        app.plugins.add(plugin)
    app.plugins.register_all(app)
    return app
