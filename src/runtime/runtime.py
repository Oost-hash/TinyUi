"""Runtime — orchestrates plugin discovery, activation, and window management."""

from __future__ import annotations

import importlib
import sys

from app_schema.manifest import (
    AppManifest, MenuSeparatorDecl, PluginManifest,
    DevToolsData, PluginInfo, SettingInfo,
)
from runtime.app_paths import AppPaths
from runtime.manifest import load_plugin_manifest
from runtime.menu import MenuRegistry, MenuItem, MenuSeparator
from runtime.persistence import SettingsRegistry, SettingsSpec
from runtime.plugin_context import PluginContext


class Runtime:
    def __init__(self) -> None:
        self._plugins: dict[str, PluginManifest] = {}
        self.paths:    AppPaths         = AppPaths.detect()
        self.settings: SettingsRegistry = SettingsRegistry(self.paths.config_dir)
        self.menu:     MenuRegistry     = MenuRegistry()

    def boot(self) -> None:
        self._load_plugin("tinyui")
        self._discover_plugins()
        self._register_settings()
        self.settings.load_persisted()
        self._register_menus()
        self._activate_plugins()

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
            for decl in plugin_manifest.menu:
                if isinstance(decl, MenuSeparatorDecl):
                    self.menu.add(decl.window, MenuSeparator(source=source))
                else:
                    self.menu.add(decl.window, MenuItem(label=decl.label, action=decl.action, source=source))

    # ── Plugin activation ─────────────────────────────────────────────────

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

    # ── Manifest queries ──────────────────────────────────────────────────

    def devtools_data(self) -> DevToolsData:
        plugins = [
            PluginInfo(
                plugin_id=plugin_id,
                plugin_type=manifest.plugin_type,
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
