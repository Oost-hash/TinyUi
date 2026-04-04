"""Runtime — orchestrates plugin discovery, activation, and window management."""

from __future__ import annotations

import sys
from pathlib import Path

from app_schema.manifest import AppManifest, PluginManifest, MenuItem as MenuItemDecl, MenuSeparator as MenuSeparatorDecl
from runtime.app.paths import AppPaths
from runtime.connectors import (
    ConnectorServiceRegistry,
    register_connector_service,
    required_connector_ids,
    unregister_connector_service,
)
from runtime.host import active_host_ids, main_window_for
from runtime_schema import (
    EventBus, EventType, PluginState, PluginStateData,
    PluginActivatedData, PluginErrorData,
    MenuRegisteredData, StatusbarRegisteredData, TabRegisteredData,
)
from runtime.manifest import load_plugin_manifest
from runtime.persistence import SettingsRegistry, SettingsSpec
from runtime.plugins.contracts import PluginContext
from runtime.plugins.packaged_plugin import resolve_packaged_plugin
from runtime.plugins.plugin_lifecycle import resolve_plugin_lifecycle
from runtime.plugins.plugin_state import PluginStateMachine


class Runtime:
    def __init__(self, event_bus: EventBus) -> None:
        self._plugins: dict[str, PluginManifest] = {}
        self._plugin_roots: dict[str, Path] = {}
        self._plugin_import_roots: set[str] = set()
        self.paths: AppPaths | None = None
        self.settings: SettingsRegistry | None = None
        self._plugin_states: dict[str, PluginStateMachine] = {}
        self._active_plugin: str | None = None  # Currently active UI plugin
        self._invalid_plugin_icons: set[str] = set()
        self.connector_services = ConnectorServiceRegistry()
        self.events = event_bus  # Use shared event bus
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
    
    def _on_ui_plugin_selected(self, event) -> None:
        """Handle user plugin selection — activate the chosen plugin."""
        self.set_active_plugin(event.data.plugin_id)

    def _on_boot_init(self, event) -> None:
        """Handle boot initialization."""
        # AppPaths.detect() handles both frozen and source modes
        self.paths = AppPaths.detect()
        self.settings = SettingsRegistry(self.paths.config_dir)
        self._boot_runtime()
        self._apply_initial_runtime_state()
    
    def _boot_runtime(self) -> None:
        """Boot runtime data, discovery, and registrations without activation policy."""
        settings = self._require_settings()
        self._load_plugin("tinyui")
        self._discover_plugins()
        self._init_plugin_states()
        self._register_settings()
        settings.load_persisted()
        self._register_menus()
        self._register_statusbar()
        self._register_tabs()

    # ── Plugin loading ────────────────────────────────────────────────────

    def _load_plugin(self, plugin_id: str) -> None:
        paths = self._require_paths()
        if plugin_id == "tinyui":
            manifest_path = paths.host_dir / "manifest.toml"
            resource_root = paths.host_dir
            self._plugin_import_roots.add(str(paths.host_dir.parent.parent))
        else:
            plugin_dir = paths.plugins_dir / plugin_id
            raw_manifest_path = plugin_dir / "manifest.toml"
            if raw_manifest_path.exists():
                manifest_path = raw_manifest_path
                resource_root = plugin_dir
                self._plugin_import_roots.add(str(plugin_dir.parent.parent))
            else:
                packaged = resolve_packaged_plugin(plugin_dir, paths)
                if packaged is None:
                    return
                manifest_path = packaged.manifest_path
                resource_root = packaged.plugin_root
                if packaged.import_root is not None:
                    self._plugin_import_roots.add(str(packaged.import_root))
        if not manifest_path.exists():
            return
        self._plugins[plugin_id] = load_plugin_manifest(manifest_path, resource_root=resource_root)
        self._plugin_roots[plugin_id] = resource_root

    def _discover_plugins(self) -> None:
        paths = self._require_paths()
        for folder in sorted(paths.plugins_dir.iterdir()):
            if not folder.is_dir() or folder.name == "tinyui":
                continue
            if (folder / "manifest.toml").exists() or (folder / "_internal" / "manifest.toml").exists():
                self._load_plugin(folder.name)

    def _plugin_root(self, plugin_id: str) -> Path:
        if plugin_id == "tinyui":
            return self._require_paths().host_dir
        return self._plugin_roots[plugin_id]

    def _plugin_icon_url(self, plugin_id: str) -> str:
        manifest = self._plugins.get(plugin_id)
        if manifest is None or not manifest.icon:
            return ""

        plugin_root = self._plugin_root(plugin_id).resolve()
        icon_path = (plugin_root / manifest.icon).resolve()
        try:
            icon_path.relative_to(plugin_root)
        except ValueError:
            self._warn_invalid_plugin_icon(
                plugin_id,
                f"resolved outside plugin root: {manifest.icon}",
            )
            return ""
        if not icon_path.exists():
            self._warn_invalid_plugin_icon(
                plugin_id,
                f"file not found: {manifest.icon}",
            )
            return ""
        self._invalid_plugin_icons.discard(plugin_id)
        return icon_path.as_uri()

    def _warn_invalid_plugin_icon(self, plugin_id: str, reason: str) -> None:
        if plugin_id in self._invalid_plugin_icons:
            return
        self._invalid_plugin_icons.add(plugin_id)
        print(f"[runtime] Ignoring invalid plugin icon for '{plugin_id}': {reason}", file=sys.stderr)

    def plugin_ids(self) -> list[str]:
        return list(self._plugins.keys())

    def plugin_manifest(self, plugin_id: str) -> PluginManifest | None:
        return self._plugins.get(plugin_id)

    def plugin_icon_url(self, plugin_id: str) -> str:
        return self._plugin_icon_url(plugin_id)

    # ── Settings registration ─────────────────────────────────────────────

    def _register_settings(self) -> None:
        settings = self._require_settings()
        paths = self._require_paths()
        for plugin_id, plugin_manifest in self._plugins.items():
            declared_keys = {s.key for s in plugin_manifest.settings}
            if "enabled" not in declared_keys:
                settings.register(plugin_id, SettingsSpec(
                    key="enabled",
                    label="Enable plugin",
                    default=True,
                    type="bool",
                ))
            for decl in plugin_manifest.settings:
                settings.register(plugin_id, SettingsSpec(
                    key=decl.key,
                    label=decl.label,
                    default=decl.default,
                    type=decl.type,
                    choices=list(decl.choices),
                ))
            # create namespace dir so persistence.save() only writes the file
            (paths.config_dir / plugin_id).mkdir(exist_ok=True)

    # ── Menu registration ─────────────────────────────────────────────────

    def _register_menus(self) -> None:
        """Register menus from manifests - emit events for UI layer."""
        for plugin_manifest in self._plugins.values():
            source = plugin_manifest.plugin_type
            for window in plugin_manifest.windows:
                for item in window.menu:
                    if isinstance(item, MenuSeparatorDecl):
                        self.events.emit_typed(EventType.MENU_REGISTERED, MenuRegisteredData(
                            window_id=window.id,
                            separator=True,
                            source=source,
                        ))
                    else:
                        self.events.emit_typed(EventType.MENU_REGISTERED, MenuRegisteredData(
                            window_id=window.id,
                            label=item.label,
                            action=item.action,
                            source=source,
                        ))
            if plugin_manifest.menu_label and plugin_manifest.plugin_menu:
                window_id = f"plugin:{plugin_manifest.plugin_id}"
                for item in plugin_manifest.plugin_menu:
                    if isinstance(item, MenuSeparatorDecl):
                        self.events.emit_typed(EventType.MENU_REGISTERED, MenuRegisteredData(
                            window_id=window_id,
                            separator=True,
                            source="plugin",
                        ))
                    else:
                        self.events.emit_typed(EventType.MENU_REGISTERED, MenuRegisteredData(
                            window_id=window_id,
                            label=item.label,
                            action=item.action,
                            source="plugin",
                        ))

    # ── Statusbar registration ────────────────────────────────────────────

    def _register_statusbar(self) -> None:
        """Register statusbar items from manifests - emit events for UI layer."""
        from app_schema.manifest import StatusbarItemDecl
        for plugin_manifest in self._plugins.values():
            source = plugin_manifest.plugin_type
            for window in plugin_manifest.windows:
                for item in window.statusbar:
                    self.events.emit_typed(EventType.STATUSBAR_REGISTERED, StatusbarRegisteredData(
                        window_id=window.id,
                        icon=item.icon,
                        text=item.text,
                        tooltip=item.tooltip,
                        action=item.action,
                        side=item.side,
                        source=source,
                    ))

    # ── Tab registration ──────────────────────────────────────────────────

    def _register_tabs(self) -> None:
        """Register tabs from manifests - emit events for UI layer."""
        for plugin_manifest in self._plugins.values():
            for tab in plugin_manifest.tabs:
                self.events.emit_typed(EventType.TAB_REGISTERED, TabRegisteredData(
                    window_id=tab.target,
                    id=tab.id,
                    label=tab.label,
                    target=tab.target,
                    surface=str(tab.surface),
                    plugin_id=tab.plugin_id,
                ))

    # ── Plugin activation ─────────────────────────────────────────────────

    def _plugin_lifecycle(self, plugin_id: str):
        """Resolve lifecycle adapter for the plugin."""
        manifest = self._plugins[plugin_id]
        return resolve_plugin_lifecycle(
            plugin_id=plugin_id,
            plugin_type=manifest.plugin_type,
            plugin_root=self._plugin_root(plugin_id),
        )

    def _active_component_ids(self) -> set[str]:
        """Return the components currently in the active state."""
        return {
            plugin_id
            for plugin_id, sm in self._plugin_states.items()
            if sm.state == PluginState.ACTIVE
        }

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
        sm = self._plugin_states.get(plugin_id)
        if sm is None:
            return False
        if target_state == PluginState.ACTIVE:
            if sm.state == PluginState.ACTIVE:
                return True
            if sm.state == PluginState.DISABLED:
                sm.transition(PluginState.ENABLING, enabling_reason)
                self._emit_plugin_state_changed(plugin_id, "disabled", "enabling")
                sm.transition(PluginState.LOADING, loading_reason)
                self._emit_plugin_state_changed(plugin_id, "enabling", "loading")
            self._load_and_activate_plugin(plugin_id)
            if sm.state == PluginState.ACTIVE and self._plugins[plugin_id].plugin_type == "connector":
                register_connector_service(
                    plugins=self._plugins,
                    connector_services=self.connector_services,
                    events=self.events,
                    plugin_id=plugin_id,
                )
            return sm.state == PluginState.ACTIVE

        if target_state != PluginState.DISABLED:
            return False
        if sm.state != PluginState.ACTIVE:
            return False
        old_state = sm.state_name
        sm.transition(PluginState.UNLOADING, unloading_reason)
        self._emit_plugin_state_changed(plugin_id, old_state, "unloading")
        if self._plugins[plugin_id].plugin_type == "connector":
            unregister_connector_service(
                connector_services=self.connector_services,
                events=self.events,
                plugin_id=plugin_id,
            )
        self._deactivate_plugin(plugin_id)
        sm.transition(PluginState.DISABLED, disabled_reason)
        self._emit_plugin_state_changed(plugin_id, "unloading", "disabled")
        return True

    def _reconcile_active_plugin(self, active_plugin: str | None, *, reason: str) -> None:
        """Reconcile runtime state for boot or active-plugin selection."""
        old_plugin = self._active_plugin
        old_connectors = required_connector_ids(self._plugins, old_plugin)
        new_connectors = required_connector_ids(self._plugins, active_plugin)
        host_ids = active_host_ids(self._plugins)

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
            if self.get_plugin_state(plugin_id) == PluginState.ACTIVE:
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

    def _ensure_plugin_import_roots(self) -> None:
        """Ensure plugin packages are importable before lifecycle activation."""
        paths = self._require_paths()
        plugins_parent = str(paths.plugins_dir.parent)
        import_roots = [plugins_parent, *sorted(self._plugin_import_roots)]
        for import_root in reversed(import_roots):
            if import_root not in sys.path:
                sys.path.insert(0, import_root)

    def _plugin_context(self, plugin_id: str) -> PluginContext:
        """Build the shared lifecycle context for a plugin."""
        return PluginContext(
            plugin_id=plugin_id,
            settings=self._require_settings().scoped(plugin_id),
            connector_services=self.connector_services,
        )

    def _emit_plugin_state_changed(self, plugin_id: str, old_state: str, new_state: str) -> None:
        """Emit the shared plugin state changed event payload."""
        self.events.emit_typed(
            EventType.PLUGIN_STATE_CHANGED,
            PluginStateData(plugin_id=plugin_id, old_state=old_state, new_state=new_state),
        )

    def _load_and_activate_plugin(self, plugin_id: str) -> None:
        """Load plugin module and activate it."""
        sm = self._plugin_states.get(plugin_id)
        if not sm:
            return

        try:
            self._plugin_lifecycle(plugin_id).activate(self._plugin_context(plugin_id))
            sm.transition(PluginState.ACTIVE, "Activation successful")
            self._emit_plugin_state_changed(plugin_id, "loading", "active")
            self.events.emit_typed(EventType.PLUGIN_ACTIVATED, PluginActivatedData(plugin_id=plugin_id))
        except Exception as e:
            sm.set_error(str(e))
            self._emit_plugin_state_changed(plugin_id, "loading", "error")
            self.events.emit_typed(EventType.PLUGIN_ERROR, PluginErrorData(plugin_id=plugin_id, error_message=str(e)))

    def _deactivate_plugin(self, plugin_id: str) -> None:
        """Deactivate a plugin."""
        try:
            self._plugin_lifecycle(plugin_id).deactivate(self._plugin_context(plugin_id))
        except Exception:
            pass  # Ignore deactivation errors

    def _apply_initial_runtime_state(self) -> None:
        """Apply the first runtime state after boot has prepared all inputs."""
        self._ensure_plugin_import_roots()
        settings = self._require_settings()
        self._reconcile_active_plugin(next(
            (
                plugin_id
                for plugin_id, manifest in self._plugins.items()
                if manifest.plugin_type == "plugin" and settings.get(plugin_id, "enabled") is not False
            ),
            None,
        ), reason="boot")

    @property
    def active_plugin(self) -> str | None:
        """Get the currently active UI plugin ID."""
        return self._active_plugin

    def set_active_plugin(self, plugin_id: str) -> bool:
        """Set the active plugin. Returns False if plugin is host or connector."""
        if plugin_id not in self._plugins:
            return False
        manifest = self._plugins[plugin_id]
        if manifest.plugin_type != "plugin":
            return False  # Host and connectors cannot be active plugin
        if self._active_plugin == plugin_id:
            return True
        self._reconcile_active_plugin(
            plugin_id,
            reason="user_selection",
        )
        return True

    # ── Plugin state management ───────────────────────────────────────────

    def _init_plugin_states(self) -> None:
        """Initialize state machines for all plugins."""
        for plugin_id in self._plugins:
            self._plugin_states[plugin_id] = PluginStateMachine(plugin_id)

    def get_plugin_state(self, plugin_id: str) -> PluginState:
        """Get current state of a plugin."""
        if plugin_id not in self._plugin_states:
            return PluginState.DISABLED
        return self._plugin_states[plugin_id].state

    def get_plugin_state_machine(self, plugin_id: str) -> PluginStateMachine | None:
        """Get state machine for a plugin."""
        return self._plugin_states.get(plugin_id)

    def enable_plugin(self, plugin_id: str) -> bool:
        """Start enabling a plugin (disabled -> enabling -> loading -> active)."""
        return self._transition_component(
            plugin_id,
            PluginState.ACTIVE,
            enabling_reason="User enabled",
            loading_reason="Loading module",
        )

    def disable_plugin(self, plugin_id: str) -> bool:
        """Disable a plugin (active -> unloading -> disabled)."""
        return self._transition_component(
            plugin_id,
            PluginState.DISABLED,
            unloading_reason="User disabled",
            disabled_reason="Disabled",
        )

    # ── Manifest queries ──────────────────────────────────────────────────

    def all_windows(self) -> list[AppManifest]:
        return [w for pm in self._plugins.values() for w in pm.windows]

    def main_window(self) -> AppManifest | None:
        return main_window_for(self._plugins)

    def window_for(self, window_id: str) -> AppManifest | None:
        return next(
            (w for w in self.all_windows() if w.id == window_id),
            None,
        )
