"""RuntimeInspector — wraps DevToolsData as a QObject for QML binding."""

from __future__ import annotations

from app_schema.manifest import DevToolsData
from PySide6.QtCore import Property, QObject, Signal


class RuntimeInspector(QObject):
    """Read-only QML view of runtime schema data. Receives DevToolsData — no runtime dependency."""
    
    dataChanged = Signal()  # Emitted when data needs refresh

    def __init__(self, data: DevToolsData, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._data = data
    
    def update_data(self, data: DevToolsData) -> None:
        """Update inspector data and notify QML."""
        self._data = data
        self.dataChanged.emit()

    @Property(list, notify=dataChanged)
    def pluginList(self) -> list[dict]:
        """Grouped plugin list for Plugin Panel: host, plugins, connectors."""
        groups = {
            "host": {"type": "host", "label": "Host", "plugins": []},
            "plugin": {"type": "plugin", "label": "Plugins", "plugins": []},
            "connector": {"type": "connector", "label": "Connectors", "plugins": []},
        }

        for info in self._data.plugins:
            plugin_data = {
                "id": info.plugin_id,
                "type": info.plugin_type,
                "version": info.version,
                "author": info.author,
                "description": info.description,
                "requires": info.requires,
                "windowCount": len(info.windows),
                "settingCount": info.setting_count,
                "state": info.state,
                "stateHistory": info.state_history,
                "errorMessage": info.error_message or "",
            }
            if info.plugin_type in groups:
                groups[info.plugin_type]["plugins"].append(plugin_data)

        # Return in fixed order: host first, then plugins, then connectors
        return [
            groups["host"],
            groups["plugin"],
            groups["connector"],
        ]

    @Property(list, notify=dataChanged)
    def pluginRows(self) -> list[dict]:
        """Flat list for the Plugins tab — sections + rows with state."""
        rows: list[dict] = []
        for info in self._data.plugins:
            # Section header with state
            state_indicator = ""
            if info.state == "active":
                state_indicator = "[active]"
            elif info.state in ("enabling", "loading"):
                state_indicator = "[loading]"
            elif info.state == "error":
                state_indicator = "[error]"
            
            rows.append({
                "rowType":  "section",
                "label":    info.plugin_id,
                "sublabel": f"{info.plugin_type} {state_indicator}".strip(),
            })
            
            # State row
            rows.append({
                "rowType": "row",
                "key":     "state",
                "value":   info.state,
                "tag":     "status",
            })
            
            # Error message if present
            if info.error_message:
                rows.append({
                    "rowType": "row",
                    "key":     "error",
                    "value":   info.error_message,
                    "tag":     "error",
                })
            
            # Windows
            for window_id, window_type in info.windows:
                rows.append({
                    "rowType": "row",
                    "key":     "window",
                    "value":   window_id,
                    "tag":     window_type,
                })
            
            # Settings count
            rows.append({
                "rowType": "row",
                "key":     "settings",
                "value":   f"{info.setting_count} declared" if info.setting_count else "none",
                "tag":     "",
            })
        return rows

    @Property(list, notify=dataChanged)
    def settingRows(self) -> list[dict]:
        """Flat list for the Settings tab — sections + rows."""
        rows: list[dict] = []
        current_ns = None
        for info in self._data.settings:
            if info.namespace != current_ns:
                current_ns = info.namespace
                rows.append({
                    "rowType":  "section",
                    "label":    info.namespace,
                    "sublabel": "",
                })
            rows.append({
                "rowType": "row",
                "key":     info.key,
                "value":   info.current_value,
                "tag":     info.type,
            })
        return rows
