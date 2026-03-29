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

"""CoreViewModel — exposes the core-owned runtime to QML."""

from PySide6.QtCore import Property, QObject, Signal, Slot
from PySide6.QtQml import QmlElement, QmlSingleton

from tinycore.logging import get_logger
from tinyruntime.core_runtime import CoreRuntime

QML_IMPORT_NAME = "TinyUI"
QML_IMPORT_MAJOR_VERSION = 1

log = get_logger(__name__)


@QmlElement
@QmlSingleton
class CoreViewModel(QObject):
    """Bridge between tinycore and QML — exposes plugin widgets, editors and settings."""

    settingsChanged    = Signal()
    settingValueChanged = Signal(str)   # emits plugin_name — voor persistence

    def __init__(self, core: CoreRuntime, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._core = core
        self._settings_cache: list[dict] | None = None

    @Property(list, constant=True)
    def widgets(self) -> list[dict]:
        """Widget list — managed by tinywidgets, not tinycore."""
        return []

    @Property(list, constant=True)
    def editors(self) -> list[dict]:
        """All registered editor specs (from plugins)."""
        return [
            {
                "id":    e.id,
                "title": e.title,
                "menu":  e.menu,
            }
            for e in self._core.host.editors.all()
        ]

    @Slot(str, bool)
    def setWidgetEnabled(self, widget_id: str, enabled: bool) -> None:
        """Widget enable/disable is handled by tinywidgets."""
        pass

    @Property(list, constant=True)
    def pluginNames(self) -> list[str]:
        """Name of each loaded plugin — used by the status bar plugin switcher."""
        return [
            participant.name
            for participant in self._core.runtime.plugin_runtime.registered_participants
        ]

    @Property(list, notify=settingsChanged)
    def settingsByPlugin(self) -> list[dict]:
        """Settings grouped by plugin and section — for the settings dialog.

        Structure: [{ plugin, sections: [{ name, settings: [{key,label,type,value,...}] }] }]
        Host settings (TinyUI) first; plugin settings below.
        Result is cached; cache is invalidated on setSettingValue.
        """
        if self._settings_cache is not None:
            return self._settings_cache

        result = []
        for plugin_name, specs in self._core.host.persistence.settings_groups():
            sections: dict[str, list[dict]] = {}
            section_order: list[str] = []
            for s in specs:
                sec = s.section or ""
                if sec not in sections:
                    sections[sec] = []
                    section_order.append(sec)
                sections[sec].append({
                    "key":         s.key,
                    "label":       s.label,
                    "type":        s.type,
                    "value":       self._core.host.persistence.get_setting(plugin_name, s.key),
                    "description": s.description,
                    "options":     s.options,
                    "min":         s.min,
                    "max":         s.max,
                    "step":        s.step,
                })
            result.append({
                "plugin":   plugin_name,
                "sections": [
                    {"name": name, "settings": sections[name]}
                    for name in section_order
                ],
            })

        log.settings("settingsByPlugin",
                     plugins=len(result),
                     structure=[(r["plugin"], [s["name"] for s in r["sections"]]) for r in result])
        self._settings_cache = result
        return result

    def _set_setting_value(self, plugin_name: str, key: str, value) -> None:
        self._core.host.persistence.set_setting(plugin_name, key, value)
        self._settings_cache = None          # invalidate cache — fresh values on next read
        self.settingsChanged.emit()
        self.settingValueChanged.emit(plugin_name)

    @Slot(str, str, str)
    def setStringSettingValue(self, plugin_name: str, key: str, value: str) -> None:
        self._set_setting_value(plugin_name, key, value)

    @Slot(str, str, bool)
    def setBoolSettingValue(self, plugin_name: str, key: str, value: bool) -> None:
        self._set_setting_value(plugin_name, key, value)

    @Slot(str, str, int)
    def setIntSettingValue(self, plugin_name: str, key: str, value: int) -> None:
        self._set_setting_value(plugin_name, key, value)

    @Slot(str, str, float)
    def setFloatSettingValue(self, plugin_name: str, key: str, value: float) -> None:
        self._set_setting_value(plugin_name, key, value)
