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

"""Write capability for runtime V2 event registration and subscriptions."""

from __future__ import annotations

from dataclasses import dataclass

from runtimeV2.events.contracts import EventBus, EventCallback, EventType
from runtimeV2.events.event_registry import EventRegistry


@dataclass
class EventSubscription:
    """Closable runtime event subscription."""

    event_type: EventType
    listener_id: int
    _bus: EventBus
    _registry: EventRegistry
    _callback: EventCallback
    _closed: bool = False

    def close(self) -> None:
        """Unsubscribe the listener from the runtime event bus."""

        if self._closed:
            return
        self._closed = True
        self._bus.off(self.event_type, self._callback)
        self._registry.unregister_listener(self.listener_id)


class EventRegistrationWrite:
    """Register runtime event contracts and event bus subscriptions."""

    def __init__(self, registry: EventRegistry, bus: EventBus) -> None:
        self._registry = registry
        self._bus = bus

    def register_event(
        self,
        owner_domain: str,
        event_type: EventType,
        description: str = "",
    ) -> None:
        """Register or replace one runtime event contract."""

        self._registry.register(event_type, domain=owner_domain, description=description)
        self._bus.emit_typed(EventType.EVENT_REGISTRY_UPDATED, data=None, source="events")

    def subscribe(
        self,
        owner_domain: str,
        event_type: EventType,
        callback: EventCallback,
        *,
        replay_history: bool = False,
        description: str = "",
    ) -> EventSubscription:
        """Register one event listener and subscribe it to the runtime event bus."""

        registration = self._registry.register_listener(
            event_type,
            domain=owner_domain,
            description=description,
        )
        self._bus.on(event_type, callback, replay_history=replay_history)
        self._bus.emit_typed(EventType.EVENT_REGISTRY_UPDATED, data=None, source="events")
        return EventSubscription(
            event_type=event_type,
            listener_id=registration.listener_id,
            _bus=self._bus,
            _registry=self._registry,
            _callback=callback,
        )
