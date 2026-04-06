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

"""Widget preview capability — manages widget preview leases for UI tabs."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Property, QObject, Signal

class WidgetPreviewCapability(QObject):
    """Manages widget preview leases for UI tabs.

    This capability allows the WidgetsTab to request a preview of a specific
    widget without actually enabling it in the overlay. The preview is shown
    in the detail pane of the WidgetsTab.
    """

    previewChanged = Signal(str)  # widget_id (empty if none)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._preview_widget_id: str = ""
        self._leases: dict[str, str] = {}  # lease_id -> widget_id

    # === QML Properties ===

    @Property(str, notify=previewChanged)
    def preview_widget_id(self) -> str:
        """Currently previewed widget ID (empty if none)."""
        return self._preview_widget_id

    # === QML Slots ===

    def request_preview(self, widget_id: str) -> str:
        """Request preview for widget. Returns lease ID."""
        if not widget_id:
            return ""
        
        # Generate simple lease ID
        lease_id = f"preview_{widget_id}_{len(self._leases)}"
        self._leases[lease_id] = widget_id
        
        # Update preview
        if self._preview_widget_id != widget_id:
            self._preview_widget_id = widget_id
            self.previewChanged.emit(widget_id)
        
        return lease_id

    def release_preview(self, lease_id: str) -> None:
        """Release preview lease."""
        if lease_id not in self._leases:
            return
        
        widget_id = self._leases.pop(lease_id)
        
        # Only clear preview if no other leases for this widget
        if self._preview_widget_id == widget_id and widget_id not in self._leases.values():
            self._preview_widget_id = ""
            self.previewChanged.emit("")

    def release_all(self) -> None:
        """Release all previews."""
        self._leases.clear()
        if self._preview_widget_id:
            self._preview_widget_id = ""
            self.previewChanged.emit("")
