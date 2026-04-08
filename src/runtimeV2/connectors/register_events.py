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

"""Event contract registration for runtime V2 connectors."""

from __future__ import annotations

from runtime_schema import EventType
from runtimeV2.events import EventRegistry


def register_connector_events(registry: EventRegistry) -> None:
    """Register connector event contracts."""

    registry.register(EventType.CONNECTOR_SERVICE_REGISTERED, domain="connectors")
    registry.register(EventType.CONNECTOR_SERVICE_UNREGISTERED, domain="connectors")
    registry.register(EventType.CONNECTOR_SERVICE_UPDATED, domain="connectors")
