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

"""ui_api action projection above runtimeV2."""

from __future__ import annotations

from collections.abc import Callable

from ui_api.api.app_actions import AppActions

from runtimeV2.contracts import (
    ConfigSetReader,
    ConfigSetWriter,
    ConnectorWriter,
    ManifestConnectorReader,
    PanelStateWriter,
    PluginActiveWriter,
    PluginDiscovery,
    RuntimeShutdownController,
    SettingsWriter,
    WidgetManualOverrideState,
    WidgetVisibilityReader,
    WidgetVisibilityWriter,
    WindowActionsWriter,
)

class UIActionsCapability:
    """Register ui_api host actions from runtime-owned capabilities."""

    def __init__(
        self,
        *,
        window_actions: WindowActionsWriter,
        manifest_connector_read: ManifestConnectorReader,
        connector_write: ConnectorWriter,
        widget_visibility_read: WidgetVisibilityReader,
        widget_visibility_write: WidgetVisibilityWriter,
        widget_manual_override: WidgetManualOverrideState,
        plugin_discovery: PluginDiscovery,
        plugin_active_write: PluginActiveWriter,
        config_set_read: ConfigSetReader,
        config_set_write: ConfigSetWriter,
        settings_write: SettingsWriter,
        panel_state_write: PanelStateWriter,
        shutdown: RuntimeShutdownController,
    ) -> None:
        self._window_actions = window_actions
        self._manifest_connector_read = manifest_connector_read
        self._connector_write = connector_write
        self._widget_visibility_read = widget_visibility_read
        self._widget_visibility_write = widget_visibility_write
        self._widget_manual_override = widget_manual_override
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
        if self._widget_manual_override.is_manually_enabled():
            self._widget_visibility_write.set_global_visible(False)
            self._release_manifest_mock_sources()
            return

        self._widget_visibility_write.set_global_visible(True)
        self._request_manifest_mock_sources()

    def _request_manifest_mock_sources(self) -> None:
        for connector_id, declaration in self._manifest_connector_read.connector_declarations().items():
            mock_source = "" if declaration.runtime is None else declaration.runtime.mock_source
            if mock_source:
                self._connector_write.request_source(connector_id, "tinyui.statusbar.widgets", mock_source)

    def _release_manifest_mock_sources(self) -> None:
        for connector_id, declaration in self._manifest_connector_read.connector_declarations().items():
            mock_source = "" if declaration.runtime is None else declaration.runtime.mock_source
            if mock_source:
                self._connector_write.release_source(connector_id, "tinyui.statusbar.widgets")

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
