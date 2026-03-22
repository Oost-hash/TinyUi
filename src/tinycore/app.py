#  TinyUI
#  Copyright (C) 2026 Oost-hash
#
#  This file is part of TinyUI.
#
#  TinyUI is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  TinyUI is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#  TinyUI builds on TinyPedal by s-victor (https://github.com/s-victor/TinyPedal),
#  licensed under GPLv3.
"""App container + create_app() factory."""

from __future__ import annotations

from pathlib import Path

from .config.loader import LoaderRegistry
from .config.store import ConfigStore
from .editor import EditorRegistry
from .events.bus import EventBus
from .plugin.registry import PluginRegistry
from .providers.registry import ProviderRegistry
from .settings import SettingsRegistry
from .telemetry.registry import ConnectorRegistry
from .widget import WidgetRegistry


class App:
    """Central application container — owns all registries."""

    def __init__(self, config_dir: Path):
        self.config        = ConfigStore()
        self.loaders       = LoaderRegistry(config_dir)
        self.connectors    = ConnectorRegistry()
        self.editors       = EditorRegistry()
        self.events        = EventBus()
        self.plugins       = PluginRegistry()
        self.providers     = ProviderRegistry()
        self.settings      = SettingsRegistry(config_dir)   # plugin settings only
        self.host_settings = SettingsRegistry(config_dir)   # host (TinyUI) — not visible to plugins
        self.widgets       = WidgetRegistry()

    def start(self, *, plugins: bool = True) -> None:
        """Start the application: emit events, optionally start all plugins.

        Pass plugins=False when using PluginLifecycleManager — it handles
        plugin start/stop on demand instead of starting everything at once.
        """
        self.events.emit("app.starting")
        if plugins:
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
