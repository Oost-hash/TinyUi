"""Settings read capability."""

from __future__ import annotations

from PySide6.QtCore import Property, QObject, Signal

from runtime.runtime import Runtime


class SettingsRead(QObject):
    """Expose settings metadata and current values sourced from runtime."""

    settingsChanged = Signal()

    def __init__(self, runtime: Runtime, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._runtime = runtime
        self._settings = self._build_settings()

    def _build_settings(self) -> list[dict]:
        registry = self._runtime.settings
        if registry is None:
            return []
        settings: list[dict] = []
        for namespace, specs in registry.by_namespace().items():
            for spec in specs:
                value = registry.get(namespace, spec.key)
                settings.append(
                    {
                        "namespace": namespace,
                        "key": spec.key,
                        "type": spec.type,
                        "currentValue": str(value if value is not None else spec.default),
                    }
                )
        return settings

    def refresh(self) -> None:
        self._settings = self._build_settings()
        self.settingsChanged.emit()

    @Property(list, notify=settingsChanged)
    def settings(self) -> list[dict]:
        return list(self._settings)
