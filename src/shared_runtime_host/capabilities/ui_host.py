"""Shared host-facing projection for runtime V2 UI chrome data."""

from __future__ import annotations

from PySide6.QtCore import QUrl

from runtimeV2.ui.capabilities.chrome_model_read import UIChromeModelRead


class UIHostCapability:
    """Project UI chrome data into host-facing shapes."""

    def __init__(self, chrome_read: UIChromeModelRead) -> None:
        self._chrome_read = chrome_read

    def tab_model(self) -> list[dict[str, str]]:
        """Return host-facing tab items."""

        return [
            {
                "id": item.tab_id,
                "label": item.label,
                "target": item.target,
                "surface": self._file_url(item.surface),
                "pluginId": item.plugin_id,
            }
            for item in self._chrome_read.tabs()
        ]

    def menu_items(self) -> list[dict[str, object]]:
        """Return host-facing menu items."""

        return [
            {
                "label": item.label,
                "action": item.action,
                "separator": item.separator,
            }
            for item in self._chrome_read.menu_items()
        ]

    def plugin_menu_items(self) -> list[dict[str, object]]:
        """Return host-facing plugin menu items."""

        return [
            {
                "label": item.label,
                "action": item.action,
                "separator": item.separator,
            }
            for item in self._chrome_read.chrome_model().plugin_menu_items
        ]

    def plugin_menu_label(self) -> str:
        """Return the host-facing plugin menu label."""

        return self._chrome_read.chrome_model().plugin_menu_label

    def left_status_items(self) -> list[dict[str, str]]:
        """Return left-side host-facing status items."""

        return [item for item in self.status_items() if item["side"] == "left"]

    def right_status_items(self) -> list[dict[str, str]]:
        """Return right-side host-facing status items."""

        return [item for item in self.status_items() if item["side"] == "right"]

    def status_items(self) -> list[dict[str, str]]:
        """Return host-facing status items."""

        return [
            {
                "icon": item.icon,
                "text": item.text,
                "tooltip": item.tooltip,
                "action": item.action,
                "side": item.side,
            }
            for item in self._chrome_read.statusbar_items()
        ]

    def active_plugin_id(self) -> str:
        """Return the active plugin id for host views."""

        return self._chrome_read.chrome_model().active_plugin_id

    def status_active_label(self) -> str:
        """Return the active status label for host views."""

        return self._chrome_read.chrome_model().status_active_label

    @staticmethod
    def _file_url(path: str) -> str:
        if not path:
            return ""
        return QUrl.fromLocalFile(path).toString()
