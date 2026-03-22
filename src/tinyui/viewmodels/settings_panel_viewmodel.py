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
"""SettingsPanelViewModel — manages the open/close state of the settings panel."""

from PySide6.QtCore import Property, QObject, Signal, Slot

from tinyui.log import get_logger

log = get_logger(__name__)


class SettingsPanelViewModel(QObject):
    openChanged            = Signal()
    settingChangeRequested = Signal(str, str, "QVariant")  # plugin, key, value

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._open: bool = False

    @Property(bool, notify=openChanged)
    def open(self) -> bool:
        return self._open

    @Slot()
    def openPanel(self) -> None:
        log.ui("openPanel")
        self._set(True)

    @Slot()
    def closePanel(self) -> None:
        log.ui("closePanel")
        self._set(False)

    @Slot()
    def togglePanel(self) -> None:
        log.ui("togglePanel", open=self._open)
        self._set(not self._open)

    @Slot(str, str, "QVariant")
    def setSetting(self, plugin_name: str, key: str, value) -> None:
        """Forward a settings change — panel has no reference to coreViewModel."""
        log.ui("setSetting", plugin=plugin_name, key=key, value=value)
        self.settingChangeRequested.emit(plugin_name, key, value)

    def _set(self, val: bool) -> None:
        if self._open != val:
            self._open = val
            self.openChanged.emit()
