"""EventBus — string-keyed pub/sub."""

from __future__ import annotations

from typing import Any, Callable


class EventBus:
    """Simple string-keyed event bus with on/emit/once."""

    def __init__(self):
        self._listeners: dict[str, list[Callable]] = {}

    def on(self, event: str, callback: Callable[..., Any]) -> Callable:
        """Subscribe to an event. Returns an unsubscribe function."""
        self._listeners.setdefault(event, []).append(callback)

        def unsubscribe():
            self._listeners[event].remove(callback)

        return unsubscribe

    def once(self, event: str, callback: Callable[..., Any]) -> Callable:
        """Subscribe to an event, auto-unsubscribe after first fire."""
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            unsubscribe()
            return callback(*args, **kwargs)

        unsubscribe = self.on(event, wrapper)
        return unsubscribe

    def emit(self, event: str, *args: Any, **kwargs: Any) -> None:
        """Fire an event. All listeners are called in registration order."""
        for callback in list(self._listeners.get(event, [])):
            callback(*args, **kwargs)
