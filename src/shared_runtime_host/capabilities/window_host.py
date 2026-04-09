"""Shared host-facing projection for runtime V2 window records."""

from __future__ import annotations

from runtimeV2.ui.capabilities.window_records_read import WindowRecordsRead
from runtimeV2.ui.contracts import UIWindowRecord


class WindowHostCapability:
    """Project UI window records into host-facing shapes."""

    def __init__(self, window_records_read: WindowRecordsRead) -> None:
        self._window_records_read = window_records_read

    def windows(self) -> list[dict[str, object]]:
        """Return all host-facing window records."""

        return [self.window(record) for record in self._window_records_read.all_window_records()]

    def window(self, record: UIWindowRecord) -> dict[str, object]:
        """Return one host-facing window record."""

        return {
            "windowId": record.window_id,
            "pluginId": record.plugin_id,
            "windowRole": record.window_role,
            "status": record.status.value,
            "visible": record.visible,
            "surface": record.surface,
            "chromeSurface": record.chrome_surface,
            "errorMessage": record.error_message,
        }
