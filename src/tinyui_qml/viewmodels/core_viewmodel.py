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

"""CoreViewModel — exposeert tinycore.App aan QML."""

from PySide6.QtCore import Property, QObject, Signal, Slot

from tinycore import App


class CoreViewModel(QObject):
    """Brug tussen tinycore en QML — exposeert plugin widgets, editors en settings."""

    settingsChanged    = Signal()
    settingValueChanged = Signal(str)   # emits plugin_name — voor persistence

    def __init__(self, core: App, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._core = core

    @Property("QVariantList", constant=True)
    def widgets(self) -> list[dict]:
        """Alle geregistreerde widget specs (vanuit plugins)."""
        return [
            {
                "id":          w.id,
                "title":       w.title,
                "description": w.description,
                "enable":      w.enable,
            }
            for w in self._core.widgets.all()
        ]

    @Property("QVariantList", constant=True)
    def editors(self) -> list[dict]:
        """Alle geregistreerde editor specs (vanuit plugins)."""
        return [
            {
                "id":    e.id,
                "title": e.title,
                "menu":  e.menu,
            }
            for e in self._core.editors.all()
        ]

    @Slot(str, bool)
    def setWidgetEnabled(self, widget_id: str, enabled: bool) -> None:
        """Zet de enable-staat van een widget in-memory. QML beheert de visuele state lokaal."""
        if self._core.widgets.has(widget_id):
            self._core.widgets.get(widget_id).enable = enabled

    @Property("QVariantList", constant=True)
    def pluginNames(self) -> list[str]:
        """Naam van elke geladen plugin — gebruikt door de statusbalk plugin-switcher."""
        return [p.name for p in self._core.plugins.plugins]

    @Property("QVariantList", notify=settingsChanged)
    def settingsByPlugin(self) -> list[dict]:
        """Settings gegroepeerd per plugin — voor de settings dialog."""
        result = []
        for plugin_name, specs in self._core.settings.by_plugin().items():
            result.append({
                "plugin": plugin_name,
                "settings": [
                    {
                        "key":         s.key,
                        "label":       s.label,
                        "type":        s.type,
                        "value":       self._core.settings.get_value(plugin_name, s.key),
                        "description": s.description,
                        "options":     s.options,
                    }
                    for s in specs
                ],
            })
        return result

    @Slot(str, str, "QVariant")
    def setSettingValue(self, plugin_name: str, key: str, value) -> None:
        """Sla een nieuwe settingswaarde op en notificeer QML en persistence."""
        self._core.settings.set_value(plugin_name, key, value)
        self.settingsChanged.emit()
        self.settingValueChanged.emit(plugin_name)
