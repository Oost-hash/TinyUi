#  TinyUI
#  Copyright (C) 2026 Oost-hash
#
#  This file is part of TinyUI.
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

"""Plugin lifecycle manager — manages enable/disable/active state of all plugins."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app_schema.plugin import PluginManifest
    from runtime.plugins.discovery import PluginDiscovery

from runtime.plugins.plugin_state import PluginStateMachine
from runtime.plugins.plugin_lifecycle import resolve_plugin_lifecycle
from runtime_schema import EventBus, EventType
from runtime_schema.plugin import PluginState


class PluginLifecycleManager:
    """Manages plugin lifecycle states and activation.

    This class is responsible for:
    - Creating state machines for all plugins
    - Enabling/disabling plugins
    - Tracking the active UI plugin
    - Coordinating plugin activation/deactivation
    """

    def __init__(
        self,
        discovery: PluginDiscovery,
        event_bus: EventBus,
    ) -> None:
        self._discovery = discovery
        self._event_bus = event_bus
        self._states: dict[str, PluginStateMachine] = {}
        self._active_plugin: str | None = None
        self._initialize_states()

    def _initialize_states(self) -> None:
        """Create state machines for all discovered plugins."""
        for plugin_id in self._discovery.list_all():
            self._states[plugin_id] = PluginStateMachine(plugin_id)

    # ── Lifecycle Control ─────────────────────────────────────────────────

    def enable(self, plugin_id: str) -> bool:
        """Enable a plugin (transition to ACTIVE).

        Args:
            plugin_id: ID of the plugin to enable.

        Returns:
            True if successful, False if plugin doesn't exist.
        """
        sm = self._states.get(plugin_id)
        if sm is None:
            return False

        manifest = self._discovery.get(plugin_id)
        if manifest is None:
            return False

        # Check dependencies
        for required_id in manifest.requires:
            required_sm = self._states.get(required_id)
            if required_sm is None or required_sm.state != PluginState.ACTIVE:
                # Auto-enable dependency
                if not self.enable(required_id):
                    return False

        # Transition through states
        if sm.state == PluginState.DISABLED:
            sm.transition(PluginState.ENABLING, "User requested enable")

        if sm.state == PluginState.ENABLING:
            # Load and activate
            try:
                self._activate_plugin(plugin_id, manifest)
                sm.transition(PluginState.LOADING, "Lifecycle activated")
            except Exception as e:
                sm.transition(PluginState.ERROR, f"Activation failed: {e}")
                return False

        if sm.state == PluginState.LOADING:
            sm.transition(PluginState.ACTIVE, "Load complete")
            self._emit_state_changed(plugin_id)

        return sm.state == PluginState.ACTIVE

    def disable(self, plugin_id: str) -> bool:
        """Disable a plugin (transition to DISABLED).

        Args:
            plugin_id: ID of the plugin to disable.

        Returns:
            True if successful, False if plugin doesn't exist.
        """
        sm = self._states.get(plugin_id)
        if sm is None:
            return False

        # Check if other plugins depend on this
        manifest = self._discovery.get(plugin_id)
        if manifest and manifest.plugin_type == "connector":
            # Find plugins that require this connector
            for other_id, other_sm in self._states.items():
                if other_id == plugin_id:
                    continue
                other_manifest = self._discovery.get(other_id)
                if other_manifest and plugin_id in other_manifest.requires:
                    if other_sm.state == PluginState.ACTIVE:
                        # Disable dependent plugin first
                        self.disable(other_id)

        # Transition to disabled
        if sm.state == PluginState.ACTIVE:
            sm.transition(PluginState.UNLOADING, "User requested disable")

        if sm.state == PluginState.UNLOADING:
            try:
                self._deactivate_plugin(plugin_id)
                sm.transition(PluginState.DISABLED, "Lifecycle deactivated")
            except Exception as e:
                sm.transition(PluginState.ERROR, f"Deactivation failed: {e}")
                return False

        self._emit_state_changed(plugin_id)
        return sm.state == PluginState.DISABLED

    def set_active(self, plugin_id: str | None) -> bool:
        """Set the active UI plugin.

        Args:
            plugin_id: ID of plugin to activate, or None to clear.

        Returns:
            True if successful.
        """
        if plugin_id is not None and plugin_id not in self._states:
            return False

        # Validate plugin can be active (must be plugin or overlay type)
        if plugin_id is not None:
            manifest = self._discovery.get(plugin_id)
            if manifest and manifest.plugin_type not in ("plugin", "overlay"):
                return False

        self._active_plugin = plugin_id

        # Emit event
        if plugin_id is not None:
            from runtime_schema.plugin import PluginActivatedData
            self._event_bus.emit_typed(
                EventType.PLUGIN_ACTIVATED,
                PluginActivatedData(plugin_id=plugin_id),
            )

        return True

    # ── Activation/Deactivation ────────────────────────────────────────────

    def _activate_plugin(self, plugin_id: str, manifest: PluginManifest) -> None:
        """Activate plugin lifecycle hooks."""
        root = self._discovery.get_root(plugin_id)
        if root is None:
            return

        lifecycle = resolve_plugin_lifecycle(
            plugin_id,
            manifest.plugin_type,
            root,
        )

        # Create minimal context (settings and connector_services would come from runtime)
        from runtime.plugins.contracts import PluginContext
        from runtime.persistence import ScopedSettings
        from runtime.connectors import ConnectorServiceRegistry

        # TODO: Get real settings and connector_services from runtime/persistence
        ctx = PluginContext(
            plugin_id=plugin_id,
            settings=ScopedSettings.__new__(ScopedSettings),  # Placeholder
            connector_services=ConnectorServiceRegistry(),  # Placeholder
        )

        lifecycle.activate(ctx)

    def _deactivate_plugin(self, plugin_id: str) -> None:
        """Deactivate plugin lifecycle hooks."""
        manifest = self._discovery.get(plugin_id)
        root = self._discovery.get_root(plugin_id)
        if manifest is None or root is None:
            return

        lifecycle = resolve_plugin_lifecycle(
            plugin_id,
            manifest.plugin_type,
            root,
        )

        from runtime.plugins.contracts import PluginContext
        from runtime.persistence import ScopedSettings
        from runtime.connectors import ConnectorServiceRegistry

        ctx = PluginContext(
            plugin_id=plugin_id,
            settings=ScopedSettings.__new__(ScopedSettings),  # Placeholder
            connector_services=ConnectorServiceRegistry(),  # Placeholder
        )

        lifecycle.deactivate(ctx)

    def _emit_state_changed(self, plugin_id: str) -> None:
        """Emit state changed event."""
        from runtime_schema.plugin import PluginStateData

        sm = self._states[plugin_id]
        # Get last transition for previous state
        old_state_name = sm.state_name
        if sm.history:
            old_state_name = sm.history[-1].from_state.name.lower()

        self._event_bus.emit_typed(
            EventType.PLUGIN_STATE_CHANGED,
            PluginStateData(
                plugin_id=plugin_id,
                new_state=sm.state_name,
                old_state=old_state_name,
            ),
        )

    # ── Accessors ─────────────────────────────────────────────────────────

    def get_state_machine(self, plugin_id: str) -> PluginStateMachine | None:
        """Get state machine for a plugin."""
        return self._states.get(plugin_id)

    def get_active(self) -> str | None:
        """Get currently active plugin ID."""
        return self._active_plugin

    def list_states(self) -> dict[str, str]:
        """Get state names for all plugins."""
        return {pid: sm.state_name for pid, sm in self._states.items()}

    def list_enabled(self) -> list[str]:
        """List all enabled (active) plugin IDs."""
        return [
            pid for pid, sm in self._states.items()
            if sm.state == PluginState.ACTIVE
        ]
