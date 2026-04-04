"""Runtime events - typed pub/sub system."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, TypeVar, Generic
from datetime import datetime
from enum import Enum, auto

T = TypeVar("T")


class EventType(Enum):
    """System event types."""
    # Boot sequence events
    BOOT_INIT = auto()      # System initialization starting
    BOOT_READY = auto()     # System ready, can open windows
    BOOT_COMPLETE = auto()  # All windows opened
    RUNTIME_SHUTDOWN = auto()
    # Plugin lifecycle events
    PLUGIN_STATE_CHANGED = auto()
    PLUGIN_ACTIVATED = auto()
    PLUGIN_DEACTIVATED = auto()
    PLUGIN_ERROR = auto()
    UI_PLUGIN_SELECTED = auto()
    UI_TAB_CHANGED = auto()
    # Connector service lifecycle events
    CONNECTOR_SERVICE_REGISTERED = auto()
    CONNECTOR_SERVICE_UNREGISTERED = auto()
    CONNECTOR_SERVICE_UPDATED = auto()
    # UI registration events - emitted by runtime, consumed by UI layer
    MENU_REGISTERED = auto()
    STATUSBAR_REGISTERED = auto()
    TAB_REGISTERED = auto()


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


@dataclass(frozen=True)
class BootInitData:
    """Data for boot.init event - passed to all components for initialization."""
    config_dir: str
    plugins_dir: str
    data_dir: str


@dataclass(frozen=True)
class BootReadyData:
    """Data for boot.ready event - system is ready for UI."""
    main_window_id: str = ""


@dataclass(frozen=True)
class MenuRegisteredData:
    """Data for menu.registered event."""
    window_id: str
    label: str = ""
    action: str = ""
    separator: bool = False
    source: str = "plugin"
    items: list[dict] = field(default_factory=list)  # For bulk registration


@dataclass(frozen=True)
class StatusbarRegisteredData:
    """Data for statusbar.registered event."""
    window_id: str
    icon: str = ""
    text: str = ""
    tooltip: str = ""
    action: str = ""
    side: str = "left"  # "left" | "right"
    source: str = "plugin"


@dataclass(frozen=True)
class TabRegisteredData:
    """Data for tab.registered event."""
    window_id: str
    id: str = ""
    label: str = ""
    target: str = ""
    surface: str = ""  # file path as string
    plugin_id: str = ""


# Callback type
EventCallback = Callable[[Event], None]


class EventBus:
    """Typed pub/sub event bus for runtime state changes."""
    
    def __init__(self) -> None:
        self._handlers: dict[EventType, list[EventCallback]] = {}
        self._history: list[Event] = []
        self._max_history = 1000
    
    def on(self, event_type: EventType, callback: EventCallback, replay_history: bool = False) -> None:
        """Register handler for specific event type.
        
        Args:
            event_type: Type of event to listen for
            callback: Handler function
            replay_history: If True, replay all historical events of this type immediately
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(callback)
        
        # Replay historical events if requested
        if replay_history:
            for event in self._history:
                if event.type == event_type:
                    try:
                        callback(event)
                    except Exception as e:
                        print(f"[EventBus] Replay handler error for {event_type}: {e}")
    
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
