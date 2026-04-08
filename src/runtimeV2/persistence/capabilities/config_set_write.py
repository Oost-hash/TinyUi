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

"""Config set write capability for runtime V2 persistence."""

from __future__ import annotations

from runtimeV2.persistence.config_sets import ConfigSetCatalog
from runtimeV2.persistence.contracts import ConfigSet


class ConfigSetWrite:
    """Write config set catalog state."""

    def __init__(self, catalog: ConfigSetCatalog) -> None:
        self._catalog = catalog

    def create_set(self, set_id: str, name: str, description: str = "") -> ConfigSet:
        """Create one config set."""

        return self._catalog.create_set(set_id, name, description)
