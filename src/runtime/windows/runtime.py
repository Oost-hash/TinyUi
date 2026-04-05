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

"""Window runtime — tracks window state and projects runtime records."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app_schema.plugin import PluginManifest
    from runtime_schema import EventBus

from runtime.ui import WindowRuntimeRecord, WindowRuntimeStatus
from runtime_schema import EventType


class WindowRuntime:
    """Manages window runtime state and projects records.

    This class is responsible for:
    - Tracking window states (opening, open, closing, closed, error)
    - Recording window errors
    - Projecting window runtime records for capabilities
    - Emitting window runtime events
    """

    def __init__(self, event_bus: EventBus) -> None:
        self._event_bus = event_bus
        self._states: dict[str, WindowRuntimeStatus] = {}
        self._errors: dict[str, str] = {}
        self._visible: dict[str, bool] = {}
        self._roles: dict[str, str] = {}  # main, dialog, etc.

    # ── State Tracking ────────────────────────────────────────────────────

    def mark_opening(self, window_id: str, role: str = "") -> None:
        """Mark window as opening."""
        self._states[window_id] = WindowRuntimeStatus.OPENING
        self._roles[window_id] = role
        self._emit_updated()

    def mark_open(self, window_id: str) -> None:
        """Mark window as open."""
        self._states[window_id] = WindowRuntimeStatus.OPEN
        self._visible[window_id] = True
        self._emit_updated()

    def mark_closing(self, window_id: str) -> None:
        """Mark window as closing."""
        if window_id in self._states:
            self._states[window_id] = WindowRuntimeStatus.CLOSING
            self._emit_updated()

    def mark_closed(self, window_id: str) -> None:
        """Mark window as closed."""
        self._states[window_id] = WindowRuntimeStatus.CLOSED
        self._visible[window_id] = False
        self._emit_updated()

    def mark_hidden(self, window_id: str) -> None:
        """Mark window as hidden (not visible but still open)."""
        self._visible[window_id] = False
        self._emit_updated()

    def mark_visible(self, window_id: str) -> None:
        """Mark window as visible."""
        self._visible[window_id] = True
        self._emit_updated()

    def mark_error(self, window_id: str, error_message: str) -> None:
        """Mark window as having an error."""
        self._states[window_id] = WindowRuntimeStatus.ERROR
        self._errors[window_id] = error_message
        self._emit_updated()

    def clear_error(self, window_id: str) -> None:
        """Clear error state for a window."""
        if window_id in self._errors:
            del self._errors[window_id]
            if self._states.get(window_id) == WindowRuntimeStatus.ERROR:
                self._states[window_id] = WindowRuntimeStatus.OPEN
            self._emit_updated()

    # ── Queries ───────────────────────────────────────────────────────────

    def get_state(self, window_id: str) -> WindowRuntimeStatus | None:
        """Get current state of a window."""
        return self._states.get(window_id)

    def get_error(self, window_id: str) -> str | None:
        """Get error message for a window."""
        return self._errors.get(window_id)

    def is_visible(self, window_id: str) -> bool:
        """Check if window is visible."""
        return self._visible.get(window_id, False)

    def get_role(self, window_id: str) -> str:
        """Get window role (main, dialog, etc.)."""
        return self._roles.get(window_id, "")

    def list_windows(self) -> list[str]:
        """List all tracked window IDs."""
        return list(self._states.keys())

    def list_open(self) -> list[str]:
        """List IDs of open windows."""
        return [
            wid for wid, state in self._states.items()
            if state in (WindowRuntimeStatus.OPEN, WindowRuntimeStatus.ERROR)
        ]

    # ── Record Projection ─────────────────────────────────────────────────

    def project_records(
        self,
        plugin_manifests: dict[str, "PluginManifest"],
    ) -> list[WindowRuntimeRecord]:
        """Project window runtime records for all tracked windows.

        Args:
            plugin_manifests: Dictionary of plugin_id -> manifest for window info.

        Returns:
            List of window runtime records.
        """
        from app_schema.plugin import PluginManifest

        records: list[WindowRuntimeRecord] = []
        for window_id, state in self._states.items():
            # Find plugin_id for this window
            plugin_id = self._find_plugin_for_window(window_id, plugin_manifests)
            role = self._roles.get(window_id, "")
            surface = self._get_surface_for_window(window_id, plugin_manifests)

            records.append(WindowRuntimeRecord(
                window_id=window_id,
                plugin_id=plugin_id or "",
                window_role=role,
                status=state,
                visible=self._visible.get(window_id, False),
                surface=surface,
                error_message=self._errors.get(window_id, ""),
            ))
        return records

    def _find_plugin_for_window(
        self,
        window_id: str,
        manifests: dict[str, "PluginManifest"],
    ) -> str | None:
        """Find which plugin owns a window."""
        for plugin_id, manifest in manifests.items():
            if manifest.ui is None:
                continue
            for window in manifest.ui.windows:
                if window.id == window_id:
                    return plugin_id
        return None

    def _get_surface_for_window(
        self,
        window_id: str,
        manifests: dict[str, "PluginManifest"],
    ) -> str:
        """Get surface path for a window."""
        for manifest in manifests.values():
            if manifest.ui is None:
                continue
            for window_decl in manifest.ui.windows:
                if window_decl.id == window_id:
                    surface = window_decl.surface
                    return str(surface) if surface else ""
        return ""

    # ── Events ────────────────────────────────────────────────────────────

    def _emit_updated(self) -> None:
        """Emit window runtime updated event."""
        from runtime_schema import WindowRuntimeUpdatedData
        self._event_bus.emit_typed(
            EventType.WINDOW_RUNTIME_UPDATED,
            WindowRuntimeUpdatedData(),
        )

    def close_all(self) -> None:
        """Mark all windows as closing (for shutdown)."""
        for window_id in list(self._states.keys()):
            if self._states[window_id] == WindowRuntimeStatus.OPEN:
                self._states[window_id] = WindowRuntimeStatus.CLOSING
        self._emit_updated()
