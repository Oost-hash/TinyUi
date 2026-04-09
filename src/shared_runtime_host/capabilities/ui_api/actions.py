"""ui_api action projection above runtimeV2."""

from __future__ import annotations

from collections.abc import Callable

from ui_api.api.app_actions import AppActions

from runtimeV2.capabilities.runtime_shutdown import RuntimeShutdown
from runtimeV2.persistence.capabilities.config_set_read import ConfigSetRead
from runtimeV2.persistence.capabilities.config_set_write import ConfigSetWrite
from runtimeV2.persistence.capabilities.settings_write import SettingsWrite
from runtimeV2.plugins.capabilities.active_write import PluginActiveWrite
from runtimeV2.plugins.capabilities.discovery import PluginDiscoveryCapability
from runtimeV2.ui.capabilities.panel_state_write import PanelStateWrite
from runtimeV2.ui.capabilities.window_actions_write import WindowActionsWrite
from runtimeV2.widgets.capabilities.widget_visibility_read import WidgetVisibilityRead
from runtimeV2.widgets.capabilities.widget_visibility_write import WidgetVisibilityWrite


class UIActionsCapability:
    """Register ui_api host actions from runtime-owned capabilities."""

    def __init__(
        self,
        *,
        window_actions: WindowActionsWrite,
        widget_visibility_read: WidgetVisibilityRead,
        widget_visibility_write: WidgetVisibilityWrite,
        plugin_discovery: PluginDiscoveryCapability,
        plugin_active_write: PluginActiveWrite,
        config_set_read: ConfigSetRead,
        config_set_write: ConfigSetWrite,
        settings_write: SettingsWrite,
        panel_state_write: PanelStateWrite,
        shutdown: RuntimeShutdown,
    ) -> None:
        self._window_actions = window_actions
        self._widget_visibility_read = widget_visibility_read
        self._widget_visibility_write = widget_visibility_write
        self._plugin_discovery = plugin_discovery
        self._plugin_active_write = plugin_active_write
        self._config_set_read = config_set_read
        self._config_set_write = config_set_write
        self._settings_write = settings_write
        self._panel_state_write = panel_state_write
        self._shutdown = shutdown

    def register(
        self,
        actions: AppActions,
        *,
        open_window: Callable[[str], None],
    ) -> None:
        """Register runtime-backed action handlers into ui_api."""

        actions.register("close", self._request_close)
        actions.register("pluginPanel.toggle", self._toggle_plugin_panel)
        actions.register("widgetVisibility.toggle", self._toggle_widget_visibility)
        actions.register("settings.saveAll", self._save_all_settings)

        for window_id in self._window_actions.openable_window_ids():
            actions.register(f"open:{window_id}", self._make_open_handler(window_id, open_window))
        for plugin_id in self._plugin_discovery.plugin_ids():
            actions.register(f"plugin.activate:{plugin_id}", self._make_activate_plugin_handler(plugin_id))
        for config_set in self._config_set_read.list_sets():
            actions.register(f"configSet.activate:{config_set.id}", self._make_activate_config_set_handler(config_set.id))

    def _make_open_handler(self, window_id: str, open_window: Callable[[str], None]) -> Callable[[], None]:
        def handler() -> None:
            if self._window_actions.request_open_window(window_id):
                open_window(window_id)

        return handler

    def _request_close(self) -> None:
        self._shutdown.begin_shutdown("main_window_close")

    def _toggle_widget_visibility(self) -> None:
        current = self._widget_visibility_read.global_visible()
        self._widget_visibility_write.set_global_visible(not current)

    def _toggle_plugin_panel(self) -> None:
        self._panel_state_write.toggle_plugin_panel()

    def _make_activate_plugin_handler(self, plugin_id: str) -> Callable[[], None]:
        def handler() -> None:
            self._plugin_active_write.set_active_plugin(plugin_id)

        return handler

    def _make_activate_config_set_handler(self, set_id: str) -> Callable[[], None]:
        def handler() -> None:
            self._config_set_write.set_active(set_id)

        return handler

    def _save_all_settings(self) -> None:
        self._settings_write.save_all()
