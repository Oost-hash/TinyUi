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

from dataclasses import dataclass

from .capabilities.registry import CapabilityRegistry
from .config.loader import LoaderRegistry
from .config.store import ConfigStore
from .paths import AppPaths
from .plugin.registry import PluginRegistry
from .session.runtime import SessionRuntime
from .settings import SettingsRegistry
from tinyui_schema import EditorRegistry


@dataclass(frozen=True)
class PersistenceServices:
    """Host-owned persistence services."""

    paths: AppPaths
    config: ConfigStore
    loaders: LoaderRegistry
    plugin_settings: SettingsRegistry
    host_settings: SettingsRegistry


@dataclass(frozen=True)
class HostServices:
    """Host-owned persistence and declaration services."""

    persistence: PersistenceServices
    editors: EditorRegistry


@dataclass(frozen=True)
class RuntimeServices:
    """Runtime-owned lifecycle and session services."""

    session: SessionRuntime
    plugins: PluginRegistry


class App:
    """Application composition container.

    ``App`` groups host services and runtime services so the composition root
    can wire the system together without exposing one flat bucket of registries.
    """

    def __init__(self, paths: AppPaths):
        self.paths = paths
        capabilities = CapabilityRegistry()
        self.host = HostServices(
            persistence=PersistenceServices(
                paths=paths,
                config=ConfigStore(),
                loaders=LoaderRegistry(paths.config_dir),
                plugin_settings=SettingsRegistry(paths.config_dir),
                host_settings=SettingsRegistry(paths.config_dir),
            ),
            editors=EditorRegistry(),
        )
        self.runtime = RuntimeServices(
            session=SessionRuntime(capabilities),
            plugins=PluginRegistry(),
        )

    def start(self, *, plugins: bool = True) -> None:
        """Start the application, optionally starting all plugins.

        Pass plugins=False when using PluginLifecycleManager — it handles
        plugin start/stop on demand instead of starting everything at once.
        """
        if plugins:
            self.runtime.plugins.start_all()

    def stop(self) -> None:
        """Stop the application and all registered plugins."""
        self.runtime.plugins.stop_all()


def create_app(paths: AppPaths, *plugins) -> App:
    """Factory: create an App, add plugins, and run register phase.

    Args:
        paths: Shared application path ownership for the current runtime mode.

    Usage:
        app = create_app(AppPaths.detect(), PluginA(), PluginB())
        app.host.persistence.loaders.load_all(app.host.persistence.config)
        app.start()
    """
    app = App(paths)
    for plugin in plugins:
        if isinstance(plugin, tuple):
            instance, requires = plugin
            app.runtime.plugins.add(instance, requires)
        else:
            app.runtime.plugins.add(plugin)
    app.runtime.plugins.register_all(app)
    return app
