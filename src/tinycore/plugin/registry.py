"""PluginRegistry — manages plugin lifecycle."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .protocol import Plugin
    from tinycore.app import App


class PluginRegistry:
    """Stores plugins and orchestrates two-phase init."""

    def __init__(self):
        self._plugins: list[Plugin] = []

    def add(self, plugin: Plugin) -> None:
        """Add a plugin to the registry."""
        self._plugins.append(plugin)

    def register_all(self, app: App) -> None:
        """Phase 1: call register() on all plugins in order."""
        for plugin in self._plugins:
            plugin.register(app)

    def start_all(self) -> None:
        """Phase 2: call start() on all plugins in order."""
        for plugin in self._plugins:
            plugin.start()

    def stop_all(self) -> None:
        """Teardown: call stop() on all plugins in reverse order."""
        for plugin in reversed(self._plugins):
            plugin.stop()

    @property
    def plugins(self) -> list[Plugin]:
        return list(self._plugins)
