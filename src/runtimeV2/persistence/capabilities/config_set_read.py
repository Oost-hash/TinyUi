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

"""Config set read capability for runtime V2 persistence."""

from __future__ import annotations

from runtimeV2.persistence.config_sets import ConfigSetCatalog
from runtimeV2.contracts import ConfigSet


class ConfigSetRead:
    """Read config set catalog state."""

    def __init__(self, catalog: ConfigSetCatalog) -> None:
        self._catalog = catalog

    def list_sets(self) -> list[ConfigSet]:
        """Return all config sets."""

        return self._catalog.list_sets()

    def active_set(self) -> ConfigSet:
        """Return the active config set."""

        return self._catalog.active_set()

    def active_set_id(self) -> str:
        """Return the active config set id."""

        return self._catalog.active_set_id()
