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

"""QML-facing image source resolver for dev/QRC dual-mode assets."""

from __future__ import annotations

from PySide6.QtCore import QObject, QUrl, Slot

from runtimeV2.paths.capabilities.path import PathCapability


class ImageSourceQmlCapability(QObject):
    """Expose image source resolution to QML for dev and frozen builds."""

    def __init__(self, paths: PathCapability, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._paths = paths

    @Slot(str, result=QUrl)
    def imageUrl(self, name: str) -> QUrl:
        """Return a QUrl for a registered image source name.

        Examples:
            imageSources.imageUrl("ui.menu")
            imageSources.imageUrl("ui.window-close")
            imageSources.imageUrl("logo.github")
        """
        try:
            return self._paths.image_source(name).to_url()
        except Exception:
            return QUrl()
