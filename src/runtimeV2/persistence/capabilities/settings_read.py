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

"""Settings read capability for runtime V2 persistence."""

from __future__ import annotations

from typing import Any

from app_schema.ui import SettingDecl
from runtimeV2.persistence.settings import SettingsStore


class SettingsRead:
    """Read setting specs and values."""

    def __init__(self, store: SettingsStore) -> None:
        self._store = store

    def get(self, namespace: str, key: str) -> Any:
        """Return one setting value."""

        return self._store.get(namespace, key)

    def by_namespace(self) -> dict[str, list[SettingDecl]]:
        """Return specs by namespace."""

        return self._store.specs_by_namespace()
