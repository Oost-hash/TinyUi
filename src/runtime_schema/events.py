"""Runtime events - typed pub/sub system."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, TypeVar, Generic
from datetime import datetime
from enum import Enum, auto

T = TypeVar("T")


class EventType(Enum):
    """System event types."""
    RUNTIME_BOOT = auto()
    RUNTIME_SHUTDOWN = auto()
    PLUGIN_STATE_CHANGED = auto()
    PLUGIN_ACTIVATED = auto()
    PLUGIN_DEACTIVATED = auto()
    PLUGIN_ERROR = auto()
    UI_PLUGIN_SELECTED = auto()
    UI_TAB_CHANGED = auto()


@dataclass(frozen=True)
class Event(Generic[T]):
    """Typed event with metadata."""
    type: EventType
    data: T
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = "runtime"


@dataclass(frozen=True)
class UIPluginSelectedData:
    """Data for ui.plugin_selected event."""
    plugin_id: str


# Callback type
EventCallback = Callable[[Event], None]


class EventBus:
    """Typed pub/sub event bus for runtime state changes."""
    
    def __init__(self) -> None:
        self._handlers: dict[EventType, list[EventCallback]] = {}
        self._history: list[Event] = []
        self._max_history = 1000
    
    def on(self, event_type: EventType, callback: EventCallback) -> None:
        """Register handler for specific event type."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(callback)
    
    def emit(self, event: Event) -> None:
        """Emit event to all registered handlers."""
        # Store in history
        self._history.append(event)
        if len(self._history) > self._max_history:
            self._history.pop(0)
        
        # Notify handlers
        handlers = self._handlers.get(event.type, [])
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                # Handler errors shouldn't break other handlers
                print(f"[EventBus] Handler error for {event.type}: {e}")
    
    def emit_typed(self, event_type: EventType, data: T, source: str = "runtime") -> Event[T]:
        """Create and emit typed event."""
        event = Event(type=event_type, data=data, source=source)
        self.emit(event)
        return event
    
    def get_history(self, event_type: EventType | None = None, limit: int = 100) -> list[Event]:
        """Get event history, optionally filtered by type."""
        events = self._history
        if event_type:
            events = [e for e in events if e.type == event_type]
        return events[-limit:]
    
    def clear_history(self) -> None:
        """Clear event history."""
        self._history.clear()
    
    def off(self, event_type: EventType, callback: EventCallback) -> None:
        """Unregister handler."""
        if event_type in self._handlers:
            self._handlers[event_type] = [
                h for h in self._handlers[event_type] if h != callback
            ]
