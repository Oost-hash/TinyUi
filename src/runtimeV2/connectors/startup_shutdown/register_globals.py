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

"""Global state registration for runtime V2 connectors."""

from __future__ import annotations

from runtimeV2.capabilities.runtime_globals import RuntimeGlobals
from runtimeV2.runtime import RuntimeV2


def register_connector_globals(runtime: RuntimeV2) -> None:
    """Register connector-owned cross-domain global states."""

    globals_capability = runtime.capability("globals", RuntimeGlobals)
    globals_capability.register_global(
        "connector_runtime",
        owner_domain="connectors",
        read_capability="connector_read",
        write_capability="connector_write",
        description="Active connector runtime surface for cross-domain reads and source control.",
    )
