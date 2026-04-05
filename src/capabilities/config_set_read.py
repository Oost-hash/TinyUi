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

"""Config set read capability."""

from __future__ import annotations

from PySide6.QtCore import Property, QObject, Signal

from runtime.persistence import ConfigSetManager


class ConfigSetRead(QObject):
    """Read config sets and active set for QML consumers."""

    setsChanged = Signal()
    activeSetChanged = Signal()

    def __init__(
        self,
        config_manager: ConfigSetManager,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._config_manager = config_manager
        self._sets = self._build_sets()
        self._active_id = config_manager.get_active_id()

    def _build_sets(self) -> list[dict[str, str]]:
        """Build list of config sets for QML."""
        return [
            {
                "id": cs.id,
                "name": cs.name,
                "description": cs.description,
                "createdAt": cs.created_at,
            }
            for cs in self._config_manager.list_sets()
        ]

    def refresh(self) -> None:
        """Refresh sets and active set from manager."""
        self._sets = self._build_sets()
        self._active_id = self._config_manager.get_active_id()
        self.setsChanged.emit()
        self.activeSetChanged.emit()

    @Property(list, notify=setsChanged)
    def sets(self) -> list[dict[str, str]]:
        """All available config sets."""
        return list(self._sets)

    @Property(str, notify=activeSetChanged)
    def activeSetId(self) -> str:
        """ID of currently active config set."""
        return self._active_id

    @Property(str, notify=activeSetChanged)
    def activeSetName(self) -> str:
        """Name of currently active config set."""
        active = self._config_manager.get_active()
        return active.name
