"""Runtime — orchestrates plugin discovery, activation, and window management."""

from __future__ import annotations

import sys
from pathlib import Path

from app_schema.manifest import AppManifest, PluginManifest, MenuItem as MenuItemDecl, MenuSeparator as MenuSeparatorDecl
from runtime.app.paths import AppPaths
from runtime.providers.provider_loader import load_provider
from runtime.providers.provider_registry import ProviderRegistry
from runtime_schema import (
    EventBus, EventType, PluginState, PluginStateData,
    PluginActivatedData, PluginErrorData,
    MenuRegisteredData, StatusbarRegisteredData, TabRegisteredData,
    ProviderRegisteredData, ProviderUnregisteredData, ProviderUpdatedData,
)
from runtime.manifest import load_plugin_manifest
from runtime.persistence import SettingsRegistry, SettingsSpec
from runtime.plugins.plugin_context import PluginContext
from runtime.plugins.plugin_lifecycle import resolve_plugin_lifecycle
from runtime.plugins.plugin_state import PluginStateMachine
from runtime_schema.plugin import PluginState


class Runtime:
    def __init__(self, event_bus: EventBus) -> None:
        self._plugins: dict[str, PluginManifest] = {}
        self.paths: AppPaths | None = None
        self.settings: SettingsRegistry | None = None
        self._plugin_states: dict[str, PluginStateMachine] = {}
        self._active_plugin: str | None = None  # Currently active UI plugin
        self._invalid_plugin_icons: set[str] = set()
        self.providers = ProviderRegistry()
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
        self._do_boot()
    
    def _do_boot(self) -> None:
        """Internal boot sequence."""
        settings = self._require_settings()
        self._load_plugin("tinyui")
        self._discover_plugins()
        self._init_plugin_states()
        self._register_settings()
        settings.load_persisted()
        self._register_menus()
        self._register_statusbar()
        self._register_tabs()
        self._init_active_plugin()

    # ── Plugin loading ────────────────────────────────────────────────────

    def _load_plugin(self, plugin_id: str) -> None:
        paths = self._require_paths()
        if plugin_id == "tinyui":
            manifest_path = paths.host_dir / "manifest.toml"
        else:
            manifest_path = paths.plugins_dir / plugin_id / "manifest.toml"
        if not manifest_path.exists():
            return
        self._plugins[plugin_id] = load_plugin_manifest(manifest_path)

    def _discover_plugins(self) -> None:
        paths = self._require_paths()
        for folder in sorted(paths.plugins_dir.iterdir()):
            if not folder.is_dir() or folder.name == "tinyui":
                continue
            if (folder / "manifest.toml").exists():
                self._load_plugin(folder.name)

    def _plugin_root(self, plugin_id: str) -> Path:
        paths = self._require_paths()
        if plugin_id == "tinyui":
            return paths.host_dir
        return paths.plugins_dir / plugin_id

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
            plugins_dir=self._require_paths().plugins_dir,
        )

    def _provider_id_for(self, plugin_id: str) -> str:
        """Map connector plugin ids to provider ids."""
        return plugin_id

    def _register_provider_for(self, plugin_id: str) -> None:
        """Instantiate and register provider for an active connector."""
        manifest = self._plugins[plugin_id]
        if not manifest.provider_module or not manifest.provider_class:
            return

        provider_id = self._provider_id_for(plugin_id)
        if self.providers.has(provider_id):
            return

        provider = load_provider(manifest.provider_module, manifest.provider_class)
        if hasattr(provider, "supports_source") and provider.supports_source("mock") and hasattr(provider, "request_source"):
            provider.request_source("__runtime__", "mock")
        if hasattr(provider, "open"):
            provider.open()
        self.providers.register(provider_id, plugin_id, manifest.plugin_id, provider)
        self.events.emit_typed(
            EventType.PROVIDER_REGISTERED,
            ProviderRegisteredData(
                provider_id=provider_id,
                plugin_id=plugin_id,
                display_name=manifest.plugin_id,
            ),
        )
        self.events.emit_typed(
            EventType.PROVIDER_UPDATED,
            ProviderUpdatedData(provider_id=provider_id, plugin_id=plugin_id),
        )

    def _unregister_provider_for(self, plugin_id: str) -> None:
        """Close and unregister provider for a connector."""
        provider_id = self._provider_id_for(plugin_id)
        provider = self.providers.get(provider_id)
        if provider is not None and hasattr(provider, "release_source"):
            provider.release_source("__runtime__")
        if provider is not None and hasattr(provider, "close"):
            provider.close()
        if self.providers.unregister(provider_id):
            self.events.emit_typed(
                EventType.PROVIDER_UNREGISTERED,
                ProviderUnregisteredData(provider_id=provider_id, plugin_id=plugin_id),
            )

    def _activate_component(self, plugin_id: str, *, enabling_reason: str, loading_reason: str) -> bool:
        """Transition a plugin or connector into the active state."""
        sm = self._plugin_states.get(plugin_id)
        if sm is None:
            return False
        if sm.state == PluginState.ACTIVE:
            return True
        if sm.state == PluginState.DISABLED:
            sm.transition(PluginState.ENABLING, enabling_reason)
            self.events.emit_typed(
                EventType.PLUGIN_STATE_CHANGED,
                PluginStateData(plugin_id=plugin_id, old_state="disabled", new_state="enabling"),
            )
            sm.transition(PluginState.LOADING, loading_reason)
            self.events.emit_typed(
                EventType.PLUGIN_STATE_CHANGED,
                PluginStateData(plugin_id=plugin_id, old_state="enabling", new_state="loading"),
            )
        self._load_and_activate_plugin(plugin_id)
        if sm.state == PluginState.ACTIVE and self._plugins[plugin_id].plugin_type == "connector":
            self._register_provider_for(plugin_id)
            self.events.emit_typed(
                EventType.PROVIDER_UPDATED,
                ProviderUpdatedData(provider_id=self._provider_id_for(plugin_id), plugin_id=plugin_id),
            )
        return sm.state == PluginState.ACTIVE

    def _deactivate_component(self, plugin_id: str, *, unloading_reason: str, disabled_reason: str) -> bool:
        """Transition a plugin or connector into the disabled state."""
        sm = self._plugin_states.get(plugin_id)
        if sm is None:
            return False
        if sm.state == PluginState.ACTIVE:
            old_state = sm.state_name
            sm.transition(PluginState.UNLOADING, unloading_reason)
            self.events.emit_typed(
                EventType.PLUGIN_STATE_CHANGED,
                PluginStateData(plugin_id=plugin_id, old_state=old_state, new_state="unloading"),
            )
            if self._plugins[plugin_id].plugin_type == "connector":
                self._unregister_provider_for(plugin_id)
            self._deactivate_plugin(plugin_id)
            sm.transition(PluginState.DISABLED, disabled_reason)
            self.events.emit_typed(
                EventType.PLUGIN_STATE_CHANGED,
                PluginStateData(plugin_id=plugin_id, old_state="unloading", new_state="disabled"),
            )
            return True
        return False

    def _required_connectors_for(self, plugin_id: str | None) -> set[str]:
        """Return connector ids required by the given UI plugin."""
        if not plugin_id:
            return set()
        manifest = self._plugins.get(plugin_id)
        if manifest is None:
            return set()
        return {
            required_id
            for required_id in manifest.requires
            if required_id in self._plugins and self._plugins[required_id].plugin_type == "connector"
        }

    def _load_and_activate_plugin(self, plugin_id: str) -> None:
        """Load plugin module and activate it."""
        sm = self._plugin_states.get(plugin_id)
        if not sm:
            return
        
        ctx = PluginContext(
            plugin_id=plugin_id,
            settings=self._require_settings().scoped(plugin_id),
            providers=self.providers,
        )
        
        try:
            self._plugin_lifecycle(plugin_id).activate(ctx)
            sm.transition(PluginState.ACTIVE, "Activation successful")
            self.events.emit_typed(EventType.PLUGIN_STATE_CHANGED, PluginStateData(
                plugin_id=plugin_id,
                old_state="loading",
                new_state="active"
            ))
            self.events.emit_typed(EventType.PLUGIN_ACTIVATED, PluginActivatedData(
                plugin_id=plugin_id
            ))
        except Exception as e:
            sm.set_error(str(e))
            self.events.emit_typed(EventType.PLUGIN_STATE_CHANGED, PluginStateData(
                plugin_id=plugin_id,
                old_state="loading",
                new_state="error"
            ))
            self.events.emit_typed(EventType.PLUGIN_ERROR, PluginErrorData(
                plugin_id=plugin_id,
                error_message=str(e)
            ))

    def _deactivate_plugin(self, plugin_id: str) -> None:
        """Deactivate a plugin."""
        ctx = PluginContext(
            plugin_id=plugin_id,
            settings=self._require_settings().scoped(plugin_id),
            providers=self.providers,
        )
        
        try:
            self._plugin_lifecycle(plugin_id).deactivate(ctx)
        except Exception:
            pass  # Ignore deactivation errors

    def _init_active_plugin(self) -> None:
        """Initialize active plugin to first enabled UI plugin (not host)."""
        paths = self._require_paths()
        settings = self._require_settings()
        plugins_parent = str(paths.plugins_dir.parent)
        if plugins_parent not in sys.path:
            sys.path.insert(0, plugins_parent)

        for plugin_id, manifest in self._plugins.items():
            if manifest.plugin_type == "plugin":  # Only UI plugins, not host or connectors
                enabled = settings.get(plugin_id, "enabled")
                if enabled is not False:  # Default to True if not set
                    self._active_plugin = plugin_id
                    break

        for plugin_id, manifest in self._plugins.items():
            if manifest.plugin_type == "host":
                self._activate_component(
                    plugin_id,
                    enabling_reason="Host enabling",
                    loading_reason="Host loading",
                )

        for connector_id in self._required_connectors_for(self._active_plugin):
            self._activate_component(
                connector_id,
                enabling_reason="Connector enabling",
                loading_reason="Connector loading",
            )

        if self._active_plugin:
            self._activate_component(
                self._active_plugin,
                enabling_reason="Boot enabling",
                loading_reason="Boot loading",
            )

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

        old_plugin = self._active_plugin
        old_connectors = self._required_connectors_for(old_plugin)
        new_connectors = self._required_connectors_for(plugin_id)

        if old_plugin:
            self._deactivate_component(
                old_plugin,
                unloading_reason="Switching plugin",
                disabled_reason="Switched away",
            )

        for connector_id in sorted(old_connectors - new_connectors):
            self._deactivate_component(
                connector_id,
                unloading_reason="Connector no longer required",
                disabled_reason="Connector released",
            )

        for connector_id in sorted(new_connectors - old_connectors):
            self._activate_component(
                connector_id,
                enabling_reason="Connector enabling",
                loading_reason="Connector loading",
            )

        self._active_plugin = plugin_id
        self._activate_component(
            plugin_id,
            enabling_reason="User enabled",
            loading_reason="Loading module",
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
        sm = self._plugin_states.get(plugin_id)
        if not sm:
            return False
        return self._activate_component(
            plugin_id,
            enabling_reason="User enabled",
            loading_reason="Loading module",
        )

    def disable_plugin(self, plugin_id: str) -> bool:
        """Disable a plugin (active -> unloading -> disabled)."""
        sm = self._plugin_states.get(plugin_id)
        if not sm:
            return False
        return self._deactivate_component(
            plugin_id,
            unloading_reason="User disabled",
            disabled_reason="Disabled",
        )

    # ── Manifest queries ──────────────────────────────────────────────────

    def all_windows(self) -> list[AppManifest]:
        return [w for pm in self._plugins.values() for w in pm.windows]

    def main_window(self) -> AppManifest | None:
        host_manifest = next(
            (manifest for manifest in self._plugins.values() if manifest.plugin_type == "host"),
            None,
        )
        if host_manifest is None or not host_manifest.windows:
            return None
        return host_manifest.windows[0]

    def window_for(self, window_id: str) -> AppManifest | None:
        return next(
            (w for w in self.all_windows() if w.id == window_id),
            None,
        )
