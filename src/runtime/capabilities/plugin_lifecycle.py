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

"""Plugin lifecycle capability — manages plugin state transitions and activation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from runtime_schema import (
    EventType,
    PluginState,
    PluginStateData,
    PluginActivatedData,
    PluginErrorData,
)
from runtime.plugins.plugin_state import PluginStateMachine

if TYPE_CHECKING:
    from runtime.runtime import Runtime


class PluginLifecycleCapability:
    """Manages plugin lifecycle states and transitions.

    Handles plugin enable/disable, activation/deactivation, and state transitions.
    Replaces the plugin lifecycle methods that were previously in Runtime.
    """

    def __init__(self) -> None:
        self._runtime: Runtime | None = None
        self._plugin_states: dict[str, PluginStateMachine] = {}
        self._active_plugin: str | None = None

    @property
    def name(self) -> str:
        """Unique capability name."""
        return "plugin_lifecycle"

    def attach(self, runtime: Runtime) -> None:
        """Attach to runtime — called on registration."""
        self._runtime = runtime

    def qml_interface(self) -> None:
        """No QML interface for this capability."""
        return None

    # ── Public API ─────────────────────────────────────────────────────────

    def get_state(self, plugin_id: str) -> PluginState:
        """Get current state of a plugin."""
        if plugin_id not in self._plugin_states:
            return PluginState.DISABLED
        return self._plugin_states[plugin_id].state

    def get_state_machine(self, plugin_id: str) -> PluginStateMachine | None:
        """Get state machine for a plugin."""
        return self._plugin_states.get(plugin_id)

    def set_active(self, plugin_id: str) -> bool:
        """Set the active UI plugin.

        Returns:
            True if successful, False if plugin not found or not a UI plugin.
        """
        if self._runtime is None:
            return False

        if plugin_id not in self._runtime.capability("plugin_discovery").all_plugins():
            return False

        manifest = self._runtime.plugin_manifest(plugin_id)
        if manifest is None or manifest.plugin_type not in {"plugin", "overlay"}:
            return False

        if self._active_plugin == plugin_id:
            return True

        self.reconcile_active_plugin(plugin_id, reason="user_selection")
        return True

    def get_active(self) -> str | None:
        """Get the currently active UI plugin ID."""
        return self._active_plugin

    def set_active_for_test(self, plugin_id: str | None) -> None:
        """Set the active plugin for testing purposes (no lifecycle activation).

        This bypasses the normal lifecycle activation and should only be used in tests.
        """
        self._active_plugin = plugin_id

    def enable(self, plugin_id: str) -> bool:
        """Start enabling a plugin (disabled -> enabling -> loading -> active).

        Returns:
            True if transition was initiated, False otherwise.
        """
        return self._transition_component(
            plugin_id,
            PluginState.ACTIVE,
            enabling_reason="User enabled",
            loading_reason="Loading module",
        )

    def disable(self, plugin_id: str) -> bool:
        """Disable a plugin (active -> unloading -> disabled).

        Returns:
            True if transition was initiated, False otherwise.
        """
        return self._transition_component(
            plugin_id,
            PluginState.DISABLED,
            unloading_reason="User disabled",
            disabled_reason="Disabled",
        )

    def initialize_states(self, plugin_ids: list[str]) -> None:
        """Initialize state machines for all plugins.

        Called during boot.
        """
        for plugin_id in plugin_ids:
            self._plugin_states[plugin_id] = PluginStateMachine(plugin_id)

    # ── Internal methods ───────────────────────────────────────────────────

    def _transition_component(
        self,
        plugin_id: str,
        target_state: PluginState,
        *,
        enabling_reason: str = "",
        loading_reason: str = "",
        unloading_reason: str = "",
        disabled_reason: str = "",
    ) -> bool:
        """Transition a component to a desired state."""
        if self._runtime is None:
            return False

        sm = self._plugin_states.get(plugin_id)
        if sm is None:
            return False

        if target_state == PluginState.ACTIVE:
            if sm.state == PluginState.ACTIVE:
                return True
            if sm.state == PluginState.DISABLED:
                sm.transition(PluginState.ENABLING, enabling_reason)
                self._emit_state_changed(plugin_id, "disabled", "enabling")
                sm.transition(PluginState.LOADING, loading_reason)
                self._emit_state_changed(plugin_id, "enabling", "loading")
            self._load_and_activate_plugin(plugin_id)
            if sm.state == PluginState.ACTIVE:
                from runtime.connectors import register_connector_service
                register_connector_service(
                    plugins=self._runtime.capability("plugin_discovery").all_plugins(),
                    connector_services=self._runtime.connector_services,
                    events=self._runtime.events,
                    plugin_id=plugin_id,
                )
            return sm.state == PluginState.ACTIVE

        if target_state != PluginState.DISABLED:
            return False
        if sm.state != PluginState.ACTIVE:
            return False

        old_state = sm.state_name
        sm.transition(PluginState.UNLOADING, unloading_reason)
        self._emit_state_changed(plugin_id, old_state, "unloading")

        from runtime.connectors import unregister_connector_service
        unregister_connector_service(
            connector_services=self._runtime.connector_services,
            events=self._runtime.events,
            plugin_id=plugin_id,
        )

        self._deactivate_plugin(plugin_id)
        sm.transition(PluginState.DISABLED, disabled_reason)
        self._emit_state_changed(plugin_id, "unloading", "disabled")
        return True

    def reconcile_active_plugin(self, active_plugin: str | None, *, reason: str) -> None:
        """Reconcile runtime state for boot or active-plugin selection."""
        if self._runtime is None:
            return

        from runtime.connectors import required_connector_ids
        from runtime.host import active_host_ids

        old_plugin = self._active_plugin
        plugins = self._runtime.capability("plugin_discovery").all_plugins()
        old_connectors = required_connector_ids(plugins, old_plugin)
        new_connectors = required_connector_ids(plugins, active_plugin)
        host_ids = active_host_ids(plugins)

        if old_plugin and old_plugin != active_plugin:
            self._transition_component(
                old_plugin,
                PluginState.DISABLED,
                unloading_reason="Switching plugin",
                disabled_reason="Switched away",
            )

        for connector_id in sorted((old_connectors - new_connectors) & self._active_component_ids()):
            self._transition_component(
                connector_id,
                PluginState.DISABLED,
                unloading_reason="Connector no longer required",
                disabled_reason="Connector released",
            )

        for plugin_id in sorted(host_ids):
            if self.get_state(plugin_id) == PluginState.ACTIVE:
                continue
            self._transition_component(
                plugin_id,
                PluginState.ACTIVE,
                enabling_reason="Host enabling",
                loading_reason="Host loading",
            )

        for connector_id in sorted(new_connectors - self._active_component_ids()):
            self._transition_component(
                connector_id,
                PluginState.ACTIVE,
                enabling_reason="Connector enabling",
                loading_reason="Connector loading",
            )

        self._active_plugin = active_plugin
        if active_plugin is not None:
            is_boot_selection = reason == "boot"
            self._transition_component(
                active_plugin,
                PluginState.ACTIVE,
                enabling_reason="Boot enabling" if is_boot_selection else "User enabled",
                loading_reason="Boot loading" if is_boot_selection else "Loading module",
            )
            # Seed widget config for overlay plugins
            manifest = self._runtime.plugin_manifest(active_plugin)
            if manifest is not None and manifest.overlay is not None:
                self._runtime.widget_store.ensure_defaults(active_plugin, manifest.overlay.widgets)

    def _active_component_ids(self) -> set[str]:
        """Return the components currently in the active state."""
        return {
            plugin_id
            for plugin_id, sm in self._plugin_states.items()
            if sm.state == PluginState.ACTIVE
        }

    def _load_and_activate_plugin(self, plugin_id: str) -> None:
        """Load plugin module and activate it."""
        if self._runtime is None:
            return

        sm = self._plugin_states.get(plugin_id)
        if not sm:
            return

        try:
            manifest = self._runtime.plugin_manifest(plugin_id)
            if manifest is not None and manifest.plugin_type == "overlay":
                self._validate_overlay_binding_sources(plugin_id)

            from runtime.plugins.plugin_lifecycle import resolve_plugin_lifecycle
            from runtime.plugins.contracts import PluginContext

            lifecycle = resolve_plugin_lifecycle(
                plugin_id=plugin_id,
                plugin_type=manifest.plugin_type if manifest else "plugin",
                plugin_root=self._runtime._plugin_root(plugin_id),
            )
            context = PluginContext(
                plugin_id=plugin_id,
                settings=self._runtime.settings.scoped(plugin_id),
                connector_services=self._runtime.connector_services,
            )
            lifecycle.activate(context)

            sm.transition(PluginState.ACTIVE, "Activation successful")
            self._emit_state_changed(plugin_id, "loading", "active")
            self._runtime.events.emit_typed(EventType.PLUGIN_ACTIVATED, PluginActivatedData(plugin_id=plugin_id))
        except Exception as e:
            sm.set_error(str(e))
            self._emit_state_changed(plugin_id, "loading", "error")
            self._runtime.events.emit_typed(EventType.PLUGIN_ERROR, PluginErrorData(plugin_id=plugin_id, error_message=str(e)))

    def _deactivate_plugin(self, plugin_id: str) -> None:
        """Deactivate a plugin."""
        if self._runtime is None:
            return

        try:
            from runtime.plugins.plugin_lifecycle import resolve_plugin_lifecycle
            from runtime.plugins.contracts import PluginContext

            manifest = self._runtime.plugin_manifest(plugin_id)
            lifecycle = resolve_plugin_lifecycle(
                plugin_id=plugin_id,
                plugin_type=manifest.plugin_type if manifest else "plugin",
                plugin_root=self._runtime._plugin_root(plugin_id),
            )
            context = PluginContext(
                plugin_id=plugin_id,
                settings=self._runtime.settings.scoped(plugin_id),
                connector_services=self._runtime.connector_services,
            )
            lifecycle.deactivate(context)
        except Exception:
            pass  # Ignore deactivation errors

    def _validate_overlay_binding_sources(self, plugin_id: str) -> None:
        """Validate that overlay bindings can be resolved from active connector services."""
        if self._runtime is None:
            return

        manifest = self._runtime.plugin_manifest(plugin_id)
        if manifest is None or manifest.overlay is None:
            return

        from runtime.connectors import required_connector_ids
        required_connectors = sorted(required_connector_ids(self._runtime.capability("plugin_discovery").all_plugins(), plugin_id))

        available_binding_keys: set[str] = set()
        for connector_id in required_connectors:
            self._runtime.connector_services.update(connector_id)
            available_binding_keys.update(key for key, _ in self._runtime.connector_services.inspect(connector_id))

        missing_keys = sorted(
            {
                binding_value
                for widget in manifest.overlay.widgets
                for binding_value in widget.bindings.values()
                if binding_value not in available_binding_keys
            }
        )
        if missing_keys:
            rendered = ", ".join(missing_keys)
            raise ValueError(f"Overlay plugin '{plugin_id}' references unavailable binding keys: {rendered}")

    def _emit_state_changed(self, plugin_id: str, old_state: str, new_state: str) -> None:
        """Emit the shared plugin state changed event payload."""
        if self._runtime is None:
            return
        self._runtime.events.emit_typed(
            EventType.PLUGIN_STATE_CHANGED,
            PluginStateData(plugin_id=plugin_id, old_state=old_state, new_state=new_state),
        )
