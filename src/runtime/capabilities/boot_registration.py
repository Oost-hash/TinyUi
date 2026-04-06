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

"""Boot registration capability — handles all boot-time registrations."""

from __future__ import annotations

from typing import TYPE_CHECKING

from runtime_schema import (
    EventType,
    MenuRegisteredData,
    StatusbarRegisteredData,
    TabRegisteredData,
    SettingsSpec,
)
from app_schema.ui import MenuItem, MenuSeparator

if TYPE_CHECKING:
    from runtime.runtime import Runtime


class BootRegistrationCapability:
    """Handles all boot-time registrations (settings, menus, statusbar, tabs).

    This capability centralizes the registration logic that was previously
    scattered across Runtime methods, making it easier to test and modify.
    """

    def __init__(self) -> None:
        self._runtime: Runtime | None = None

    @property
    def name(self) -> str:
        """Unique capability name."""
        return "boot_registration"

    def attach(self, runtime: Runtime) -> None:
        """Attach to runtime — called on registration."""
        self._runtime = runtime

    def qml_interface(self) -> None:
        """No QML interface for this capability."""
        return None

    def register_all(self) -> None:
        """Register all manifest declarations (settings, menus, statusbar, tabs).
        
        Must be called after plugin discovery so manifests are available.
        """
        self._register_settings()
        self._register_menus()
        self._register_statusbar()
        self._register_tabs()

    def _register_settings(self) -> None:
        """Register settings from all plugin manifests."""
        if self._runtime is None:
            return

        settings = self._runtime.settings
        paths = self._runtime.paths
        for plugin_id, plugin_manifest in self._runtime.capability("plugin_discovery").all_plugins().items():
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
            # Create namespace dir so persistence.save() only writes the file
            if paths is not None:
                from pathlib import Path
                (Path(paths.config_dir) / plugin_id).mkdir(exist_ok=True)

    def _register_menus(self) -> None:
        """Register menus from all plugin manifests."""
        if self._runtime is None:
            return

        for plugin_manifest in self._runtime.capability("plugin_discovery").all_plugins().values():
            source = plugin_manifest.plugin_type
            windows = [] if plugin_manifest.ui is None else plugin_manifest.ui.windows
            for window in windows:
                for item in window.menu:
                    self._emit_menu_item(window.id, item, source)

            if plugin_manifest.ui and plugin_manifest.ui.menu_label and plugin_manifest.ui.plugin_menu:
                window_id = f"plugin:{plugin_manifest.plugin_id}"
                for item in plugin_manifest.ui.plugin_menu:
                    self._emit_menu_item(window_id, item, "plugin")

    def _emit_menu_item(self, window_id: str, item: MenuItem | MenuSeparator, source: str) -> None:
        """Emit a single menu item registration event."""
        if self._runtime is None:
            return

        if isinstance(item, MenuSeparator):
            self._runtime.events.emit_typed(
                EventType.MENU_REGISTERED,
                MenuRegisteredData(window_id=window_id, separator=True, source=source)
            )
        else:
            self._runtime.events.emit_typed(
                EventType.MENU_REGISTERED,
                MenuRegisteredData(
                    window_id=window_id,
                    label=item.label,
                    action=item.action,
                    source=source,
                )
            )

    def _register_statusbar(self) -> None:
        """Register statusbar items from all plugin manifests."""
        if self._runtime is None:
            return

        for plugin_manifest in self._runtime.capability("plugin_discovery").all_plugins().values():
            source = plugin_manifest.plugin_type
            windows = [] if plugin_manifest.ui is None else plugin_manifest.ui.windows
            for window in windows:
                for item in window.statusbar:
                    self._runtime.events.emit_typed(
                        EventType.STATUSBAR_REGISTERED,
                        StatusbarRegisteredData(
                            window_id=window.id,
                            icon=item.icon,
                            text=item.text,
                            tooltip=item.tooltip,
                            action=item.action,
                            side=item.side,
                            source=source,
                        )
                    )

    def _register_tabs(self) -> None:
        """Register tabs from all plugin manifests."""
        if self._runtime is None:
            return

        for plugin_manifest in self._runtime.capability("plugin_discovery").all_plugins().values():
            tabs = [] if plugin_manifest.ui is None else plugin_manifest.ui.tabs
            for tab in tabs:
                self._runtime.events.emit_typed(
                    EventType.TAB_REGISTERED,
                    TabRegisteredData(
                        window_id=tab.target,
                        id=tab.id,
                        label=tab.label,
                        target=tab.target,
                        surface=str(tab.surface),
                        plugin_id=tab.plugin_id,
                    )
                )
