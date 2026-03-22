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

"""CoreViewModel — exposes tinycore.App to QML."""

from PySide6.QtCore import Property, QObject, Signal, Slot

from tinycore import App
from tinyui.log import get_logger

log = get_logger(__name__)


class CoreViewModel(QObject):
    """Bridge between tinycore and QML — exposes plugin widgets, editors and settings."""

    settingsChanged    = Signal()
    settingValueChanged = Signal(str)   # emits plugin_name — voor persistence

    def __init__(self, core: App, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._core = core
        self._settings_cache: list[dict] | None = None

    @Property("QVariantList", constant=True)
    def widgets(self) -> list[dict]:
        """All registered widget specs (from plugins)."""
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
        """All registered editor specs (from plugins)."""
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
        """Set a widget's enabled state in memory. QML manages visual state locally."""
        if self._core.widgets.has(widget_id):
            self._core.widgets.get(widget_id).enable = enabled

    @Property("QVariantList", constant=True)
    def pluginNames(self) -> list[str]:
        """Name of each loaded plugin — used by the status bar plugin switcher."""
        return [p.name for p in self._core.plugins.plugins]

    @Property("QVariantList", notify=settingsChanged)
    def settingsByPlugin(self) -> list[dict]:
        """Settings grouped by plugin and section — for the settings dialog.

        Structure: [{ plugin, sections: [{ name, settings: [{key,label,type,value,...}] }] }]
        Host settings (TinyUI) first; plugin settings below.
        Result is cached; cache is invalidated on setSettingValue.
        """
        if self._settings_cache is not None:
            return self._settings_cache

        result = []
        # Host settings first (TinyUI), then plugin settings
        registries = [self._core.host_settings, self._core.settings]
        for registry in registries:
            for plugin_name, specs in registry.by_plugin().items():
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
                        "value":       registry.get_value(plugin_name, s.key),
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

    @Slot(str, str, "QVariant")
    def setSettingValue(self, plugin_name: str, key: str, value) -> None:
        """Persist a new setting value and notify QML."""
        registry = (
            self._core.host_settings
            if self._core.host_settings.has_plugin(plugin_name)
            else self._core.settings
        )
        registry.set_value(plugin_name, key, value)
        self._settings_cache = None          # invalidate cache — fresh values on next read
        self.settingsChanged.emit()
        self.settingValueChanged.emit(plugin_name)
