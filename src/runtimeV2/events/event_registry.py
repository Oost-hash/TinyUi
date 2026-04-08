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

"""Event registry for runtime V2 event contracts."""

from __future__ import annotations

from dataclasses import dataclass

from runtime_schema import EventType


@dataclass(frozen=True)
class EventContract:
    """Registered event contract owned by one domain."""

    event_type: EventType
    domain: str
    description: str = ""


class EventRegistry:
    """Registry of known runtime V2 event contracts."""

    def __init__(self) -> None:
        self._contracts: dict[EventType, EventContract] = {}

    def register(
        self,
        event_type: EventType,
        *,
        domain: str,
        description: str = "",
    ) -> None:
        """Register or replace an event contract."""

        self._contracts[event_type] = EventContract(
            event_type=event_type,
            domain=domain,
            description=description,
        )

    def events(self) -> list[EventContract]:
        """Return all registered event contracts."""

        return list(self._contracts.values())

    def events_for_domain(self, domain: str) -> list[EventContract]:
        """Return registered events for one domain."""

        return [contract for contract in self._contracts.values() if contract.domain == domain]

    def event(self, event_type: EventType) -> EventContract | None:
        """Return one event contract if it is registered."""

        return self._contracts.get(event_type)
