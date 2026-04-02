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


class Runtime:
    def __init__(self) -> None:
        self._plugins: dict[str, PluginManifest] = {}
        self.paths:     AppPaths          = AppPaths.detect()
        self.settings:  SettingsRegistry  = SettingsRegistry(self.paths.config_dir)
        self.menu:      MenuRegistry      = MenuRegistry()
        self.statusbar: StatusbarRegistry = StatusbarRegistry()
        self._active_plugin: str | None = None  # Currently active UI plugin

    def boot(self) -> None:
        self._load_plugin("tinyui")
        self._discover_plugins()
        self._register_settings()
        self.settings.load_persisted()
        self._register_menus()
        self._register_statusbar()
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
                    break

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
        self._active_plugin = plugin_id
        self.statusbar.set_active_plugin(plugin_id)
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
