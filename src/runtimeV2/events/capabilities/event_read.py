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

"""Read capability for runtime V2 event contracts."""

from __future__ import annotations

from runtimeV2.contracts import EventType
from runtimeV2.events.event_registry import EventContract, EventListenerRegistration, EventRegistry


class EventRead:
    """Read registered runtime V2 event contracts."""

    def __init__(self, registry: EventRegistry) -> None:
        self._registry = registry

    def events(self) -> list[EventContract]:
        """Return all registered event contracts."""

        return self._registry.events()

    def events_for_domain(self, domain: str) -> list[EventContract]:
        """Return registered events for one domain."""

        return self._registry.events_for_domain(domain)

    def event(self, event_type: EventType) -> EventContract | None:
        """Return one event contract if it is registered."""

        return self._registry.event(event_type)

    def listeners(self) -> list[EventListenerRegistration]:
        """Return registered event listeners."""

        return self._registry.listeners()

    def listeners_for_event(self, event_type: EventType) -> list[EventListenerRegistration]:
        """Return registered listeners for one event type."""

        return self._registry.listeners_for_event(event_type)

    def listeners_for_domain(self, domain: str) -> list[EventListenerRegistration]:
        """Return registered listeners for one owner domain."""

        return self._registry.listeners_for_domain(domain)
