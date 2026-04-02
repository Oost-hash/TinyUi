"""Runtime — orchestrates plugin discovery, activation, and window management."""

from __future__ import annotations

import importlib
import sys

from app_schema.manifest import (
    AppManifest, PluginManifest, MenuItem as MenuItemDecl, MenuSeparator as MenuSeparatorDecl,
    DevToolsData, PluginInfo, SettingInfo,
)
from runtime.app_paths import AppPaths
from runtime.manifest import load_plugin_manifest
from runtime.menu import MenuRegistry, MenuItem, MenuSeparator
from runtime.persistence import SettingsRegistry, SettingsSpec
from runtime.plugin_context import PluginContext
from runtime.statusbar import StatusbarRegistry, StatusbarItem
from runtime.plugin_state import PluginState, PluginStateMachine
from runtime.tabs import TabRegistry


class Runtime:
    def __init__(self) -> None:
        self._plugins: dict[str, PluginManifest] = {}
        self.paths:     AppPaths          = AppPaths.detect()
        self.settings:  SettingsRegistry  = SettingsRegistry(self.paths.config_dir)
        self.menu:      MenuRegistry      = MenuRegistry()
        self.statusbar: StatusbarRegistry = StatusbarRegistry()
        self.tabs:      TabRegistry       = TabRegistry()
        self._plugin_states: dict[str, PluginStateMachine] = {}
        self._active_plugin: str | None = None  # Currently active UI plugin

    def boot(self) -> None:
        self._load_plugin("tinyui")
        self._discover_plugins()
        self._init_plugin_states()
        self._register_settings()
        self.settings.load_persisted()
        self._register_menus()
        self._register_statusbar()
        self._register_tabs()
        self._activate_plugins()
        self._init_active_plugin()

    # ── Plugin loading ────────────────────────────────────────────────────

    def _load_plugin(self, plugin_id: str) -> None:
        manifest_path = self.paths.plugins_dir / plugin_id / "manifest.toml"
        if not manifest_path.exists():
            return
        self._plugins[plugin_id] = load_plugin_manifest(manifest_path)

    def _discover_plugins(self) -> None:
        for folder in sorted(self.paths.plugins_dir.iterdir()):
            if not folder.is_dir() or folder.name == "tinyui":
                continue
            if (folder / "manifest.toml").exists():
                self._load_plugin(folder.name)

    # ── Settings registration ─────────────────────────────────────────────

    def _register_settings(self) -> None:
        for plugin_id, plugin_manifest in self._plugins.items():
            declared_keys = {s.key for s in plugin_manifest.settings}
            if "enabled" not in declared_keys:
                self.settings.register(plugin_id, SettingsSpec(
                    key="enabled",
                    label="Enable plugin",
                    default=True,
                    type="bool",
                ))
            for decl in plugin_manifest.settings:
                self.settings.register(plugin_id, SettingsSpec(
                    key=decl.key,
                    label=decl.label,
                    default=decl.default,
                    type=decl.type,
                    choices=list(decl.choices),
                ))
            # create namespace dir so persistence.save() only writes the file
            (self.paths.config_dir / plugin_id).mkdir(exist_ok=True)

    # ── Menu registration ─────────────────────────────────────────────────

    def _register_menus(self) -> None:
        for plugin_manifest in self._plugins.values():
            source = plugin_manifest.plugin_type
            for window in plugin_manifest.windows:
                for item in window.menu:
                    if isinstance(item, MenuSeparatorDecl):
                        self.menu.add(window.id, MenuSeparator(source=source))
                    else:
                        self.menu.add(window.id, MenuItem(label=item.label, action=item.action, source=source))
            if plugin_manifest.menu_label and plugin_manifest.plugin_menu:
                window_id = f"plugin:{plugin_manifest.plugin_id}"
                for item in plugin_manifest.plugin_menu:
                    if isinstance(item, MenuSeparatorDecl):
                        self.menu.add(window_id, MenuSeparator(source="plugin"))
                    else:
                        self.menu.add(window_id, MenuItem(label=item.label, action=item.action, source="plugin"))

    # ── Plugin activation ─────────────────────────────────────────────────

    def _register_statusbar(self) -> None:
        """Register statusbar items from manifests."""
        from app_schema.manifest import StatusbarItemDecl
        for plugin_manifest in self._plugins.values():
            source = plugin_manifest.plugin_type
            for window in plugin_manifest.windows:
                for item in window.statusbar:
                    self.statusbar.add(window.id, StatusbarItem(
                        icon=item.icon,
                        text=item.text,
                        tooltip=item.tooltip,
                        action=item.action,
                        side=item.side,  # type: ignore
                        source=source,
                    ))

    def _register_tabs(self) -> None:
        """Register tabs from manifests."""
        for plugin_manifest in self._plugins.values():
            for tab in plugin_manifest.tabs:
                self.tabs.register(tab.target, tab)

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
        
        # Start transition: disabled -> enabling
        if not sm.transition(PluginState.ENABLING, "User enabled"):
            return False
        
        # Continue to loading immediately
        sm.transition(PluginState.LOADING, "Loading module")
        
        # Actually load and activate the plugin
        self._load_and_activate_plugin(plugin_id)
        return True

    def disable_plugin(self, plugin_id: str) -> bool:
        """Disable a plugin (active -> unloading -> disabled)."""
        sm = self._plugin_states.get(plugin_id)
        if not sm:
            return False
        
        current = sm.state
        if current == PluginState.ACTIVE:
            sm.transition(PluginState.UNLOADING, "User disabled")
            self._deactivate_plugin(plugin_id)
        
        sm.transition(PluginState.DISABLED, "Disabled")
        return True

    def _load_and_activate_plugin(self, plugin_id: str) -> None:
        """Load plugin module and activate it."""
        sm = self._plugin_states.get(plugin_id)
        if not sm:
            return
        
        ctx = PluginContext(
            plugin_id=plugin_id,
            settings=self.settings.scoped(plugin_id),
        )
        
        try:
            mod = importlib.import_module(f"plugins.{plugin_id}.plugin")
            if hasattr(mod, "activate"):
                mod.activate(ctx)
            sm.transition(PluginState.ACTIVE, "Activation successful")
        except Exception as e:
            sm.set_error(str(e))

    def _deactivate_plugin(self, plugin_id: str) -> None:
        """Deactivate a plugin."""
        ctx = PluginContext(
            plugin_id=plugin_id,
            settings=self.settings.scoped(plugin_id),
        )
        
        try:
            mod = importlib.import_module(f"plugins.{plugin_id}.plugin")
            if hasattr(mod, "deactivate"):
                mod.deactivate(ctx)
        except Exception:
            pass  # Ignore deactivation errors

    def _activate_plugins(self) -> None:
        plugins_parent = str(self.paths.plugins_dir.parent)
        if plugins_parent not in sys.path:
            sys.path.insert(0, plugins_parent)

        for plugin_id in self._plugins:
            ctx = PluginContext(
                plugin_id=plugin_id,
                settings=self.settings.scoped(plugin_id),
            )
            try:
                mod = importlib.import_module(f"plugins.{plugin_id}.plugin")
                if hasattr(mod, "activate"):
                    mod.activate(ctx)
            except ModuleNotFoundError:
                pass

    def _init_active_plugin(self) -> None:
        """Initialize active plugin to first enabled UI plugin (not host)."""
        for plugin_id, manifest in self._plugins.items():
            if manifest.plugin_type == "plugin":  # Only UI plugins, not host or connectors
                enabled = self.settings.get(plugin_id, "enabled")
                if enabled is not False:  # Default to True if not set
                    self._active_plugin = plugin_id
                    self.statusbar.set_active_plugin(plugin_id)
                    self.tabs.set_active_plugin(plugin_id)
                    break
        
        # Initialize state machines for all plugins
        for plugin_id, manifest in self._plugins.items():
            sm = self._plugin_states.get(plugin_id)
            if not sm:
                continue
            
            if plugin_id == self._active_plugin:
                # Active UI plugin - transition through all states quickly
                if sm.state == PluginState.DISABLED:
                    sm.transition(PluginState.ENABLING, "Boot enabling")
                    sm.transition(PluginState.LOADING, "Boot loading")
                    sm.transition(PluginState.ACTIVE, "Boot active")
            elif manifest.plugin_type == "host":
                # Host is always conceptually active
                if sm.state == PluginState.DISABLED:
                    sm.transition(PluginState.ENABLING, "Host enabling")
                    sm.transition(PluginState.LOADING, "Host loading")
                    sm.transition(PluginState.ACTIVE, "Host active")
            elif manifest.plugin_type == "connector":
                # Check if connector is used by active plugin
                if self._active_plugin:
                    active_manifest = self._plugins.get(self._active_plugin)
                    if active_manifest and plugin_id in active_manifest.requires:
                        if sm.state == PluginState.DISABLED:
                            sm.transition(PluginState.ENABLING, "Connector enabling")
                            sm.transition(PluginState.LOADING, "Connector loading")
                            sm.transition(PluginState.ACTIVE, "Connector in use")
            # Other plugins stay disabled

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
        
        # Deactivate old plugin
        if self._active_plugin and self._active_plugin != plugin_id:
            old_sm = self._plugin_states.get(self._active_plugin)
            if old_sm and old_sm.state == PluginState.ACTIVE:
                old_sm.transition(PluginState.UNLOADING, "Switching plugin")
                self._deactivate_plugin(self._active_plugin)
                old_sm.transition(PluginState.DISABLED, "Switched away")
        
        # Activate new plugin
        self._active_plugin = plugin_id
        self.statusbar.set_active_plugin(plugin_id)
        self.tabs.set_active_plugin(plugin_id)
        
        new_sm = self._plugin_states.get(plugin_id)
        if new_sm and new_sm.state == PluginState.DISABLED:
            new_sm.transition(PluginState.ENABLING, "User enabled")
            new_sm.transition(PluginState.LOADING, "Loading module")
            self._load_and_activate_plugin(plugin_id)
        
        return True

    # ── Manifest queries ──────────────────────────────────────────────────

    def devtools_data(self) -> DevToolsData:
        plugins = [
            PluginInfo(
                plugin_id=plugin_id,
                plugin_type=manifest.plugin_type,
                version=manifest.version,
                author=manifest.author,
                description=manifest.description,
                requires=manifest.requires,
                windows=[(w.id, w.window_type) for w in manifest.windows],
                setting_count=len(manifest.settings),
                state=self._plugin_states.get(plugin_id, PluginStateMachine(plugin_id)).state_name,
                state_history=[
                    {
                        "from": t.from_state.name.lower(),
                        "to": t.to_state.name.lower(),
                        "time": t.timestamp,
                        "reason": t.reason,
                    }
                    for t in self._plugin_states.get(plugin_id, PluginStateMachine(plugin_id)).history
                ],
                error_message=self._plugin_states.get(plugin_id, PluginStateMachine(plugin_id)).error_message,
            )
            for plugin_id, manifest in self._plugins.items()
        ]
        settings = [
            SettingInfo(
                namespace=namespace,
                key=spec.key,
                type=spec.type,
                current_value=str(self.settings.get(namespace, spec.key) if self.settings.get(namespace, spec.key) is not None else spec.default),
            )
            for namespace, specs in self.settings.by_namespace().items()
            for spec in specs
        ]
        return DevToolsData(plugins=plugins, settings=settings)

    @property
    def plugin_menus(self) -> dict[str, list[dict]]:
        result: dict[str, list[dict]] = {}
        for pm in self._plugins.values():
            if pm.menu_label and pm.plugin_menu:
                window_id = f"plugin:{pm.plugin_id}"
                result[pm.menu_label] = self.menu.to_qml(window_id)
        return result

    def all_windows(self) -> list[AppManifest]:
        return [w for pm in self._plugins.values() for w in pm.windows]

    def main_window(self) -> AppManifest | None:
        return next(
            (w for w in self.all_windows() if w.window_type == "main"),
            None,
        )

    def window_for(self, window_id: str) -> AppManifest | None:
        return next(
            (w for w in self.all_windows() if w.id == window_id),
            None,
        )
