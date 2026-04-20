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

"""Runtime-owned QML context for hosted windows."""

from __future__ import annotations

from collections.abc import Mapping

from PySide6.QtCore import Property, QObject


class RuntimeQmlContext(QObject):
    """Expose runtime/domain capabilities as one QML object."""

    def __init__(self, properties: dict[str, object], parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._properties = dict(properties)
        self._property_names = tuple(self._properties)

    @property
    def property_names(self) -> tuple[str, ...]:
        """Return the context property names for diagnostics and tests."""

        return self._property_names

    def _object_property(self, name: str) -> QObject | None:
        value = self._properties.get(name)
        return value if isinstance(value, QObject) else None

    @property
    def properties(self) -> Mapping[str, object]:
        """Return the raw context objects for Python-side inspection."""

        return self._properties

    @Property(QObject, constant=True)
    def connectorActions(self) -> QObject | None:
        return self._object_property("connectorActions")

    @Property(QObject, constant=True)
    def connectorRead(self) -> QObject | None:
        return self._object_property("connectorRead")

    @Property(QObject, constant=True)
    def imageSources(self) -> QObject | None:
        return self._object_property("imageSources")

    @Property(QObject, constant=True)
    def manifestRead(self) -> QObject | None:
        return self._object_property("manifestRead")

    @Property(QObject, constant=True)
    def panelState(self) -> QObject | None:
        return self._object_property("panelState")

    @Property(QObject, constant=True)
    def pluginActive(self) -> QObject | None:
        return self._object_property("pluginActive")

    @Property(QObject, constant=True)
    def pluginState(self) -> QObject | None:
        return self._object_property("pluginState")

    @Property(QObject, constant=True)
    def renderStatus(self) -> QObject | None:
        return self._object_property("renderStatus")

    @Property(QObject, constant=True)
    def settingsRead(self) -> QObject | None:
        return self._object_property("settingsRead")

    @Property(QObject, constant=True)
    def settingsWrite(self) -> QObject | None:
        return self._object_property("settingsWrite")

    @Property(QObject, constant=True)
    def uiChrome(self) -> QObject | None:
        return self._object_property("uiChrome")

    @Property(QObject, constant=True)
    def widgetConfigRead(self) -> QObject | None:
        return self._object_property("widgetConfigRead")

    @Property(QObject, constant=True)
    def widgetConfigWrite(self) -> QObject | None:
        return self._object_property("widgetConfigWrite")

    @Property(QObject, constant=True)
    def widgetPreviewActions(self) -> QObject | None:
        return self._object_property("widgetPreviewActions")

    @Property(QObject, constant=True)
    def widgetRecords(self) -> QObject | None:
        return self._object_property("widgetRecords")

    @Property(QObject, constant=True)
    def widgetVisibility(self) -> QObject | None:
        return self._object_property("widgetVisibility")

    @Property(QObject, constant=True)
    def windowRecords(self) -> QObject | None:
        return self._object_property("windowRecords")
