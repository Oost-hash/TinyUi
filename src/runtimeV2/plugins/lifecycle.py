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

"""Plugin lifecycle state for runtime V2."""

from __future__ import annotations

from runtime_schema import EventType, PluginActivatedData, PluginDeactivatedData, PluginState, PluginStateData
from runtimeV2.connectors.policy import register_connector_service, unregister_connector_service
from runtimeV2.connectors.startup import ConnectorsStartupResult
from runtimeV2.events import EventsStartupResult
from runtimeV2.plugins.registry import PluginRegistry


class PluginLifecycleStore:
    """Store plugin lifecycle state and active plugin policy."""

    def __init__(
        self,
        *,
        registry: PluginRegistry,
        connectors: ConnectorsStartupResult,
        events: EventsStartupResult,
    ) -> None:
        self._registry = registry
        self._connectors = connectors
        self._events = events
        self._states: dict[str, PluginState] = {
            plugin_id: PluginState.DISABLED
            for plugin_id in registry.plugin_ids()
        }
        self._active_plugin: str | None = None
        self._activate_hosts()

    def get_active_plugin(self) -> str | None:
        """Return the active plugin or overlay."""

        return self._active_plugin

    def set_active_plugin(self, plugin_id: str) -> bool:
        """Set the active plugin or overlay."""

        manifest = self._registry.manifest(plugin_id)
        if manifest is None or manifest.plugin_type not in {"plugin", "overlay"}:
            return False
        if self._active_plugin == plugin_id:
            return True
        if self._active_plugin is not None:
            self.disable_plugin(self._active_plugin)
        self._active_plugin = plugin_id
        return self.enable_plugin(plugin_id)

    def get_plugin_state(self, plugin_id: str) -> PluginState:
        """Return one plugin lifecycle state."""

        return self._states.get(plugin_id, PluginState.DISABLED)

    def enable_plugin(self, plugin_id: str) -> bool:
        """Enable one plugin lifecycle component."""

        manifest = self._registry.manifest(plugin_id)
        if manifest is None:
            return False

        if manifest.plugin_type == "connector":
            register_connector_service(
                manifest=manifest,
                connector_services=self._connectors.registry,
            )

        self._set_state(plugin_id, PluginState.ACTIVE)
        self._events.bus.emit_typed(
            EventType.PLUGIN_ACTIVATED,
            PluginActivatedData(plugin_id=plugin_id),
            source="plugins",
        )
        return True

    def disable_plugin(self, plugin_id: str) -> bool:
        """Disable one plugin lifecycle component."""

        manifest = self._registry.manifest(plugin_id)
        if manifest is None:
            return False

        if manifest.plugin_type == "connector":
            unregister_connector_service(
                manifest=manifest,
                connector_services=self._connectors.registry,
            )

        self._set_state(plugin_id, PluginState.DISABLED)
        if self._active_plugin == plugin_id:
            self._active_plugin = None
        self._events.bus.emit_typed(
            EventType.PLUGIN_DEACTIVATED,
            PluginDeactivatedData(plugin_id=plugin_id),
            source="plugins",
        )
        return True

    def _activate_hosts(self) -> None:
        for plugin_id, manifest in self._registry.all_manifests().items():
            if manifest.plugin_type == "host":
                self._set_state(plugin_id, PluginState.ACTIVE)

    def _set_state(self, plugin_id: str, new_state: PluginState) -> None:
        old_state = self._states.get(plugin_id, PluginState.DISABLED)
        self._states[plugin_id] = new_state
        if old_state == new_state:
            return
        self._events.bus.emit_typed(
            EventType.PLUGIN_STATE_CHANGED,
            PluginStateData(
                plugin_id=plugin_id,
                old_state=old_state.name.lower(),
                new_state=new_state.name.lower(),
            ),
            source="plugins",
        )
