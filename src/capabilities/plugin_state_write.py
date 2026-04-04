"""Plugin state write capability."""

from __future__ import annotations

from PySide6.QtCore import QObject, Slot

from runtime.runtime import Runtime


class PluginStateWrite(QObject):
    """QML-facing write surface for plugin lifecycle controls."""

    def __init__(self, runtime: Runtime, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._runtime = runtime

    @Slot(str, result=bool)
    def enablePlugin(self, plugin_id: str) -> bool:
        return self._runtime.enable_plugin(plugin_id)

    @Slot(str, result=bool)
    def disablePlugin(self, plugin_id: str) -> bool:
        return self._runtime.disable_plugin(plugin_id)
