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

"""Runtime V2 event contracts and event bus."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Callable, Generic, TypeVar

T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)


class EventType(Enum):
    """Runtime V2 event types."""

    RUNTIME_SHUTDOWN = auto()
    DOMAIN_REGISTERED = auto()
    DOMAIN_STARTING = auto()
    DOMAIN_READY = auto()
    DOMAIN_ERROR = auto()
    DOMAIN_STOPPED = auto()
    EVENT_REGISTRY_UPDATED = auto()
    PLUGINS_DISCOVERED = auto()
    PLUGIN_STATE_CHANGED = auto()
    PLUGIN_ACTIVATED = auto()
    PLUGIN_DEACTIVATED = auto()
    PLUGIN_ERROR = auto()
    CONNECTOR_SERVICE_REGISTERED = auto()
    CONNECTOR_SERVICE_UNREGISTERED = auto()
    CONNECTOR_SERVICE_UPDATED = auto()
    CONNECTOR_SOURCE_CHANGED = auto()
    CONNECTOR_GAME_DETECTED = auto()
    CONNECTOR_GAME_LOST = auto()
    SCHEDULER_JOB_REGISTERED = auto()
    SCHEDULER_JOB_UPDATED = auto()
    SCHEDULER_CLOCK_UPDATED = auto()
    SCHEDULER_TICK = auto()
    UI_READY = auto()
    UI_RENDER_BLOCKED = auto()
    UI_WINDOW_RECORDS_CHANGED = auto()
    UI_PANEL_VISIBILITY_CHANGED = auto()
    WIDGET_RUNTIME_UPDATED = auto()
    WIDGET_VISIBILITY_CHANGED = auto()


@dataclass(frozen=True)
class Event(Generic[T_co]):
    """Typed runtime V2 event with metadata."""

    type: EventType
    data: T_co
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = "runtime"


EventCallback = Callable[[Event[object]], None]


class EventBus:
    """Typed pub/sub event bus for runtime V2 state changes."""

    def __init__(self) -> None:
        self._handlers: dict[EventType, list[EventCallback]] = {}
        self._history: list[Event[object]] = []
        self._max_history = 1000

    def on(self, event_type: EventType, callback: EventCallback, replay_history: bool = False) -> None:
        """Register a handler for one event type."""

        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(callback)

        if replay_history:
            for event in self._history:
                if event.type == event_type:
                    callback(event)

    def emit(self, event: Event[object]) -> None:
        """Emit an event to all registered handlers."""

        self._history.append(event)
        if len(self._history) > self._max_history:
            self._history.pop(0)

        handlers = self._handlers.get(event.type, [])
        for handler in handlers:
            handler(event)

    def emit_typed(self, event_type: EventType, data: T, source: str = "runtime") -> Event[T]:
        """Create and emit a typed event."""

        event = Event(type=event_type, data=data, source=source)
        self.emit(event)
        return event

    def get_history(self, event_type: EventType | None = None, limit: int = 100) -> list[Event[object]]:
        """Return event history, optionally filtered by type."""

        events = self._history
        if event_type:
            events = [event for event in events if event.type == event_type]
        return events[-limit:]

    def clear_history(self) -> None:
        """Clear event history."""

        self._history.clear()

    def off(self, event_type: EventType, callback: EventCallback) -> None:
        """Unregister one event handler."""

        if event_type in self._handlers:
            self._handlers[event_type] = [
                handler
                for handler in self._handlers[event_type]
                if handler != callback
            ]
