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

"""Widget management capability — manages widget runtime records and projection."""

from __future__ import annotations

from typing import TYPE_CHECKING

from runtime.widgets import WidgetRuntimeRecord, project_overlay_widget_records

if TYPE_CHECKING:
    from runtime.runtime import Runtime


class WidgetManagementCapability:
    """Manages widget runtime records and projection for overlay plugins.

    This capability centralizes widget-related logic that was previously
    in Runtime, making it easier to extend with future widget features
    (positioning, visibility rules, binding updates, etc.).
    """

    def __init__(self) -> None:
        self._runtime: Runtime | None = None

    @property
    def name(self) -> str:
        """Unique capability name."""
        return "widget_management"

    def attach(self, runtime: Runtime) -> None:
        """Attach to runtime — called on registration."""
        self._runtime = runtime

    def qml_interface(self) -> None:
        """No QML interface for this capability."""
        return None

    def overlay_widget_records(self, plugin_id: str) -> list[WidgetRuntimeRecord]:
        """Return runtime-owned widget records for one overlay plugin."""
        if self._runtime is None:
            return []

        from runtime.capabilities.widget_visibility import WidgetVisibilityCapability
        widget_visibility = self._runtime.capability("widget_visibility")
        discovery = self._runtime.capability("plugin_discovery")

        return project_overlay_widget_records(
            discovery.all_plugins(),
            self._runtime.connector_services,
            plugin_id=plugin_id,
            active_plugin=self._runtime.active_plugin,
            global_visible=widget_visibility.globalVisible,
            widget_store=self._runtime.widget_store,
        )

    def active_overlay_widget_records(self) -> list[WidgetRuntimeRecord]:
        """Return widget records for the currently active overlay."""
        if self._runtime is None:
            return []

        if self._runtime._shutdown_requested:
            return []

        active = self._runtime.active_plugin
        if active is None:
            return []

        discovery = self._runtime.capability("plugin_discovery")
        manifest = discovery.plugin_manifest(active)
        if manifest is None or manifest.plugin_type != "overlay":
            return []

        return self.overlay_widget_records(active)
