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

"""Runtime — orchestrates plugin discovery, activation, and window management."""

from __future__ import annotations

from pathlib import Path

from app_schema.plugin import PluginManifest
from app_schema.ui import AppManifest
from runtime.app.paths import AppPaths
from runtime.connectors import ConnectorServiceRegistry
from runtime.host import main_window_for
from runtime_schema import (
    EventBus, EventType, PluginState, PluginStateData,
    RuntimeShutdownData,
    WindowRuntimeUpdatedData,
)
from runtime.persistence import SettingsRegistry, WidgetConfigStore, ConfigSetManager

from widget_api import WidgetRegistry, create_default_widget_registry
from runtime.plugins.plugin_state import PluginStateMachine
from runtime.ui import WindowRuntimeRecord, WindowRuntimeStatus, project_window_records
from runtime.widgets import WidgetRuntimeRecord, project_overlay_widget_records

from PySide6.QtCore import QObject


class Runtime:
    def __init__(
        self,
        event_bus: EventBus,
        settings: SettingsRegistry,
        widget_store: WidgetConfigStore,
        config_manager: ConfigSetManager,
        connector_registry: ConnectorServiceRegistry | None = None,
        widget_registry: WidgetRegistry | None = None,
        plugin_discovery: object | None = None,
        plugin_lifecycle: object | None = None,
        window_runtime: object | None = None,
    ) -> None:
        self.paths: AppPaths | None = None
        self.settings: SettingsRegistry = settings
        self.widget_store: WidgetConfigStore = widget_store
        self.config_manager: ConfigSetManager = config_manager


        self._shutdown_requested = False
        self.connector_services: ConnectorServiceRegistry = connector_registry or ConnectorServiceRegistry()
        self.widget_registry: WidgetRegistry = widget_registry or create_default_widget_registry()
        # New domain components (optional during migration)
        self.plugin_discovery = plugin_discovery
        self.plugin_lifecycle = plugin_lifecycle
        self.window_runtime = window_runtime
        self.events = event_bus  # Use shared event bus
        # Capability registry
        self._capabilities: dict[str, object] = {}
        self._qml_capabilities: dict[str, QObject] = {}
        self._register_default_capabilities()
        self._subscribe_to_events()

    def _require_paths(self) -> AppPaths:
        assert self.paths is not None, "Runtime paths are unavailable before BOOT_INIT"
        return self.paths

    def _require_settings(self) -> SettingsRegistry:
        assert self.settings is not None, "Runtime settings are unavailable before BOOT_INIT"
        return self.settings
    
    def _subscribe_to_events(self) -> None:
        """Subscribe to boot and UI events."""
        self.events.on(EventType.BOOT_INIT, self._on_boot_init)
        self.events.on(EventType.UI_PLUGIN_SELECTED, self._on_ui_plugin_selected)

    def _register_default_capabilities(self) -> None:
        """Register default runtime capabilities."""
        from runtime.capabilities.widget_visibility import WidgetVisibilityCapability
        from runtime.capabilities.window_state import WindowStateCapability
        from runtime.capabilities.plugin_icon import PluginIconCapability
        from runtime.capabilities.boot_registration import BootRegistrationCapability
        from runtime.capabilities.plugin_lifecycle import PluginLifecycleCapability
        from runtime.capabilities.plugin_discovery import PluginDiscoveryCapability

        self.register(PluginDiscoveryCapability())  # Must be first - other capabilities depend on it
        self.register(WidgetVisibilityCapability())
        self.register(WindowStateCapability())
        self.register(PluginIconCapability())
        self.register(BootRegistrationCapability())
        self.register(PluginLifecycleCapability())

    def register(self, capability: object) -> None:
        """Register a capability with the runtime.

        Args:
            capability: Object implementing the RuntimeCapability protocol.
        """
        self._capabilities[capability.name] = capability
        capability.attach(self)
        qml_iface = capability.qml_interface()
        if qml_iface is not None:
            self._qml_capabilities[capability.name] = qml_iface

    def capability(self, name: str) -> object:
        """Get a registered capability by name.

        Args:
            name: The capability name.

        Returns:
            The capability instance.

        Raises:
            KeyError: If capability not found.
        """
        if name not in self._capabilities:
            raise KeyError(f"Capability '{name}' not found")
        return self._capabilities[name]

    def qml_capabilities(self) -> dict[str, QObject]:
        """Get all QML-capable interfaces.

        Returns:
            Dictionary mapping capability names to QML interfaces.
        """
        return dict(self._qml_capabilities)
    
    def _on_ui_plugin_selected(self, event) -> None:
        """Handle user plugin selection — activate the chosen plugin."""
        self.set_active_plugin(event.data.plugin_id)

    def _on_boot_init(self, event) -> None:
        """Handle boot initialization."""
        # AppPaths.detect() handles both frozen and source modes
        self.paths = AppPaths.detect()
        self._boot_runtime()
        # Load persisted settings after registration (done by BootRegistrationCapability)
        self.settings.load_persisted()
        self._apply_initial_runtime_state()
    
    def _boot_runtime(self) -> None:
        """Boot runtime data, discovery, and registrations without activation policy."""
        discovery = self.capability("plugin_discovery")
        discovery.load_plugin("tinyui")
        discovery.discover_plugins()
        # Initialize plugin states via capability
        self.capability("plugin_lifecycle").initialize_states(discovery.plugin_ids())
        # Register settings, menus, statusbar, tabs from manifests
        # (Must happen after plugin discovery so manifests are available)
        self.capability("boot_registration").register_all()

    # ── Plugin discovery (delegated to capability) ────────────────────────

    def plugin_ids(self) -> list[str]:
        """Get all loaded plugin IDs."""
        discovery = self.capability("plugin_discovery")
        return discovery.plugin_ids()

    def plugin_manifest(self, plugin_id: str) -> PluginManifest | None:
        """Get manifest for a loaded plugin."""
        discovery = self.capability("plugin_discovery")
        return discovery.plugin_manifest(plugin_id)

    def _plugin_root(self, plugin_id: str) -> Path:
        """Get resource root for a loaded plugin."""
        discovery = self.capability("plugin_discovery")
        root = discovery.plugin_root(plugin_id)
        if root is None:
            raise KeyError(f"Plugin '{plugin_id}' not found")
        return root

    def plugin_icon_url(self, plugin_id: str) -> str:
        """Get icon URL for a plugin."""
        return self.capability("plugin_icon").get_icon_url(plugin_id)

    def overlay_widget_records(self, plugin_id: str) -> list[WidgetRuntimeRecord]:
        """Return runtime-owned widget records for one overlay plugin."""
        widget_visibility = self.capability("widget_visibility")
        discovery = self.capability("plugin_discovery")
        return project_overlay_widget_records(
            discovery.all_plugins(),
            self.connector_services,
            plugin_id=plugin_id,
            active_plugin=self.active_plugin,
            global_visible=widget_visibility.globalVisible,
            widget_store=self.widget_store,
        )

    def active_overlay_widget_records(self) -> list[WidgetRuntimeRecord]:
        """Return widget records for the currently active overlay."""
        if self._shutdown_requested:
            return []
        active = self.active_plugin
        if active is None:
            return []
        discovery = self.capability("plugin_discovery")
        manifest = discovery.plugin_manifest(active)
        if manifest is None or manifest.plugin_type != "overlay":
            return []
        return self.overlay_widget_records(active)

    def window_records(self) -> list[WindowRuntimeRecord]:
        """Return runtime-owned records for manifest-declared application windows."""
        window_state = self.capability("window_state")
        discovery = self.capability("plugin_discovery")
        return window_state.project_records(discovery.all_plugins())

    def window_record(self, window_id: str) -> WindowRuntimeRecord | None:
        """Return one runtime-owned window record by id."""
        return next((record for record in self.window_records() if record.window_id == window_id), None)

    def mark_window_opening(self, window_id: str, plugin_id: str = "") -> None:
        """Record that a window handoff to ui_api has started."""
        self.capability("window_state").mark_opening(window_id)

    def mark_window_open(self, window_id: str, plugin_id: str = "") -> None:
        """Record that a window is open."""
        self.capability("window_state").mark_open(window_id)

    def mark_window_hidden(self, window_id: str) -> None:
        """Record that a window remains hosted but hidden."""
        self.capability("window_state").mark_hidden(window_id)

    def mark_window_closing(self, window_id: str) -> None:
        """Record that a window is in the shutdown or close handoff."""
        self.capability("window_state").mark_closing(window_id)

    def mark_window_closed(self, window_id: str) -> None:
        """Record that a window has been closed."""
        self.capability("window_state").mark_closed(window_id)

    def mark_window_error(self, window_id: str, message: str) -> None:
        """Record that a window failed to open or close correctly."""
        self.capability("window_state").mark_error(window_id, message)

    def begin_shutdown(self, reason: str = "app_quit") -> None:
        """Project shutdown intent onto all currently hosted windows."""
        if self._shutdown_requested:
            return
        self._shutdown_requested = True
        self.events.emit_typed(EventType.RUNTIME_SHUTDOWN, RuntimeShutdownData(reason=reason))
        for record in self.window_records():
            if record.status in {WindowRuntimeStatus.OPEN, WindowRuntimeStatus.OPENING, WindowRuntimeStatus.HIDDEN}:
                self.mark_window_closing(record.window_id)

    # ── Settings registration ─────────────────────────────────────────────

    # ── Plugin activation ─────────────────────────────────────────────────

    def _ensure_plugin_import_roots(self) -> None:
        """Ensure plugin packages are importable before lifecycle activation."""
        discovery = self.capability("plugin_discovery")
        discovery.ensure_import_roots()

    def _apply_initial_runtime_state(self) -> None:
        """Apply the first runtime state after boot has prepared all inputs."""
        self._ensure_plugin_import_roots()
        settings = self._require_settings()
        lifecycle = self.capability("plugin_lifecycle")
        discovery = self.capability("plugin_discovery")
        if lifecycle is not None:
            lifecycle.reconcile_active_plugin(
                active_plugin=next(
                (
                    plugin_id
                    for plugin_id, manifest in discovery.all_plugins().items()
                    if manifest.plugin_type in {"plugin", "overlay"} and settings.get(plugin_id, "enabled") is not False
                ),
                None,
            ), reason="boot")

    @property
    def active_plugin(self) -> str | None:
        """Get the currently active UI plugin ID."""
        lifecycle = self.capability("plugin_lifecycle")
        if lifecycle is None:
            return None
        return lifecycle.get_active()

    def set_active_plugin(self, plugin_id: str) -> bool:
        """Set the active UI component. Returns False for non-UI plugin types."""
        lifecycle = self.capability("plugin_lifecycle")
        if lifecycle is None:
            return False
        return lifecycle.set_active(plugin_id)

    # ── Plugin state management (delegated to capability) ─────────────────

    def get_plugin_state(self, plugin_id: str) -> PluginState:
        """Get current state of a plugin."""
        lifecycle = self.capability("plugin_lifecycle")
        if lifecycle is None:
            return PluginState.DISABLED
        return lifecycle.get_state(plugin_id)

    def get_plugin_state_machine(self, plugin_id: str) -> PluginStateMachine | None:
        """Get state machine for a plugin."""
        lifecycle = self.capability("plugin_lifecycle")
        if lifecycle is None:
            return None
        return lifecycle.get_state_machine(plugin_id)

    def enable_plugin(self, plugin_id: str) -> bool:
        """Start enabling a plugin (disabled -> enabling -> loading -> active)."""
        lifecycle = self.capability("plugin_lifecycle")
        if lifecycle is None:
            return False
        return lifecycle.enable(plugin_id)

    def disable_plugin(self, plugin_id: str) -> bool:
        """Disable a plugin (active -> unloading -> disabled)."""
        lifecycle = self.capability("plugin_lifecycle")
        if lifecycle is None:
            return False
        return lifecycle.disable(plugin_id)

    # ── Manifest queries ──────────────────────────────────────────────────

    def all_windows(self) -> list[AppManifest]:
        discovery = self.capability("plugin_discovery")
        return [w for pm in discovery.all_plugins().values() for w in ([] if pm.ui is None else pm.ui.windows)]

    def main_window(self) -> AppManifest | None:
        discovery = self.capability("plugin_discovery")
        return main_window_for(discovery.all_plugins())

    def window_for(self, window_id: str) -> AppManifest | None:
        return next(
            (w for w in self.all_windows() if w.id == window_id),
            None,
        )
