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

"""Shared widget preview actions above runtime-owned widget visibility."""

from __future__ import annotations

from PySide6.QtCore import QObject, Slot

from runtimeV2.contracts import (
    ConnectorWriter,
    ManifestConnectorReader,
    WidgetManualOverrideState,
    WidgetVisibilityReader,
    WidgetVisibilityWriter,
)

_WIDGET_PREVIEW_OWNER = "tinyui.statusbar.widgets"


class WidgetPreviewActions(QObject):
    """Compose widget preview visibility with manifest mock connector sources."""

    def __init__(
        self,
        *,
        manifest_connector_read: ManifestConnectorReader,
        connector_write: ConnectorWriter,
        widget_visibility_read: WidgetVisibilityReader,
        widget_visibility_write: WidgetVisibilityWriter,
        widget_manual_override: WidgetManualOverrideState,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._manifest_connector_read = manifest_connector_read
        self._connector_write = connector_write
        self._widget_visibility_read = widget_visibility_read
        self._widget_visibility_write = widget_visibility_write
        self._widget_manual_override = widget_manual_override

    def set_preview_visible(self, visible: bool) -> None:
        """Set widget preview visibility and keep connector mock sources in sync."""

        if visible:
            self._widget_visibility_write.clear_focus()
            self._widget_visibility_write.set_global_visible(True)
            self._request_manifest_mock_sources()
            return

        self._widget_visibility_write.clear_focus()
        self._widget_visibility_write.set_global_visible(False)
        self._release_manifest_mock_sources()

    def set_focused_preview_visible(self, overlay_id: str, widget_id: str, visible: bool) -> None:
        """Set widget preview visibility for one focused widget."""

        if not visible:
            self._release_manifest_mock_sources()
            return

        self._widget_visibility_write.focus_widget(overlay_id, widget_id)
        self._widget_visibility_write.set_global_visible(True)
        self._request_manifest_mock_sources()

    def set_focused_widget_visible(self, overlay_id: str, widget_id: str, visible: bool) -> None:
        """Set only one focused widget visible without changing connector mock sources."""

        if not visible:
            self._widget_visibility_write.clear_focus()
            self._widget_visibility_write.set_global_visible(False)
            return

        self._widget_visibility_write.focus_widget(overlay_id, widget_id)
        self._widget_visibility_write.set_global_visible(True)

    def toggle_preview_visible(self) -> None:
        """Toggle widget preview visibility using runtime manual override state."""

        self.set_preview_visible(not self._widget_manual_override.is_manually_enabled())

    def preview_visible(self) -> bool:
        """Return the runtime-owned global widget visibility state."""

        return self._widget_visibility_read.global_visible()

    @Slot(bool)
    def setPreviewVisible(self, visible: bool) -> None:
        """Set widget preview visibility from QML."""

        self.set_preview_visible(visible)

    @Slot(str, str, bool)
    def setFocusedPreviewVisible(self, overlay_id: str, widget_id: str, visible: bool) -> None:
        """Set widget preview visibility for one focused widget from QML."""

        self.set_focused_preview_visible(overlay_id, widget_id, visible)

    @Slot(str, str, bool)
    def setFocusedWidgetVisible(self, overlay_id: str, widget_id: str, visible: bool) -> None:
        """Set only one focused widget visible from QML."""

        self.set_focused_widget_visible(overlay_id, widget_id, visible)

    @Slot()
    def togglePreviewVisible(self) -> None:
        """Toggle widget preview visibility from QML."""

        self.toggle_preview_visible()

    def _request_manifest_mock_sources(self) -> None:
        for connector_id, declaration in self._manifest_connector_read.connector_declarations().items():
            mock_source = "" if declaration.runtime is None else declaration.runtime.mock_source
            if mock_source:
                self._connector_write.request_source(connector_id, _WIDGET_PREVIEW_OWNER, mock_source)

    def _release_manifest_mock_sources(self) -> None:
        for connector_id, declaration in self._manifest_connector_read.connector_declarations().items():
            mock_source = "" if declaration.runtime is None else declaration.runtime.mock_source
            if mock_source:
                self._connector_write.release_source(connector_id, _WIDGET_PREVIEW_OWNER)
