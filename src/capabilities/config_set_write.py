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

"""Config set write capability."""

from __future__ import annotations

from PySide6.QtCore import QObject, Slot

from runtime.persistence import ConfigSetManager


class ConfigSetWrite(QObject):
    """Write config sets and switch active set for QML consumers."""

    def __init__(
        self,
        config_manager: ConfigSetManager,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._config_manager = config_manager

    @Slot(str, result=bool)
    def setActiveSet(self, set_id: str) -> bool:
        """Switch to another config set (effective after restart).

        Args:
            set_id: ID of the config set to activate.

        Returns:
            True if successful, False if set does not exist.
        """
        return self._config_manager.set_active(set_id)

    @Slot(str, str, result=bool)
    def createSet(self, set_id: str, name: str) -> bool:
        """Create a new config set.

        Args:
            set_id: Unique ID for the new set.
            name: Display name for the new set.

        Returns:
            True if created, False if ID already exists or invalid.
        """
        result = self._config_manager.create_set(set_id, name)
        return result is not None

    @Slot(str, str, result=bool)
    def createSetWithDescription(
        self,
        set_id: str,
        name: str,
        description: str,
    ) -> bool:
        """Create a new config set with description.

        Args:
            set_id: Unique ID for the new set.
            name: Display name for the new set.
            description: Description of the set.

        Returns:
            True if created, False if ID already exists or invalid.
        """
        result = self._config_manager.create_set(set_id, name, description)
        return result is not None

    @Slot(str, result=bool)
    def deleteSet(self, set_id: str) -> bool:
        """Delete a config set.

        Cannot delete the default set or the currently active set.

        Args:
            set_id: ID of the set to delete.

        Returns:
            True if deleted, False if cannot delete.
        """
        return self._config_manager.delete_set(set_id)

    @Slot(str, str, result=bool)
    def renameSet(self, set_id: str, new_name: str) -> bool:
        """Rename a config set.

        Args:
            set_id: ID of the set to rename.
            new_name: New display name.

        Returns:
            True if renamed, False if set does not exist.
        """
        return self._config_manager.rename_set(set_id, new_name)
