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
"""Application-level info exposed to QML as a singleton."""

from __future__ import annotations

from PySide6.QtCore import QObject, Property
from PySide6.QtQml import QmlElement, QmlSingleton

QML_IMPORT_NAME = "TinyUI"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
@QmlSingleton
class AppInfo(QObject):

    def __init__(self, app_name: str, devtools_available: bool, devtools_path: str,
                 parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._app_name = app_name
        self._devtools_available = devtools_available
        self._devtools_path = devtools_path

    @Property(str, constant=True)
    def appName(self) -> str:
        return self._app_name

    @Property(bool, constant=True)
    def devToolsAvailable(self) -> bool:
        return self._devtools_available

    @Property(str, constant=True)
    def devToolsQmlPath(self) -> str:
        return self._devtools_path
