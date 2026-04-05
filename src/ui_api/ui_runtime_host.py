"""Qt host controllers that bridge runtime-owned window state to live QML windows."""

from __future__ import annotations

from typing import Any, Protocol

from runtime_schema import EventBus, EventType, StartupResult, startup_ok


class WindowRuntimeLike(Protocol):
    """Minimal runtime surface needed by the Qt window host bridge."""

    def mark_window_open(self, window_id: str) -> None: ...
    def mark_window_closed(self, window_id: str) -> None: ...
    def begin_shutdown(self, reason: str = "app_quit") -> None: ...


def attach_window_runtime_tracking(runtime: WindowRuntimeLike, window_id: str, qml_window) -> None:
    """Mirror basic Qt window visibility back into runtime-owned window state."""

    if hasattr(qml_window, "destroyed"):
        qml_window.destroyed.connect(lambda *_args: runtime.mark_window_closed(window_id))
    if hasattr(qml_window, "visibleChanged"):
        qml_window.visibleChanged.connect(
            lambda visible: runtime.mark_window_open(window_id) if visible else runtime.mark_window_closed(window_id)
        )


def attach_main_window_shutdown(runtime: WindowRuntimeLike, qml_window) -> None:
    """Treat main-window close or hide as an application shutdown request."""

    if hasattr(qml_window, "destroyed"):
        qml_window.destroyed.connect(lambda *_args: runtime.begin_shutdown("main_window_destroyed"))
    if hasattr(qml_window, "visibleChanged"):
        qml_window.visibleChanged.connect(
            lambda visible: None if visible else runtime.begin_shutdown("main_window_hidden")
        )


class WindowHostController:
    """Keep hosted application windows aligned with runtime shutdown intent."""

    def __init__(self, event_bus: EventBus) -> None:
        self._event_bus = event_bus
        self._handles: dict[str, Any] = {}

    def attach(self) -> None:
        self._event_bus.on(EventType.RUNTIME_SHUTDOWN, self._on_shutdown)

    def track(self, window_id: str, handle) -> None:
        self._handles[window_id] = handle

    def _on_shutdown(self, _event) -> None:
        for _window_id, handle in list(self._handles.items()):
            qml_window = handle.qml_window
            if hasattr(qml_window, "close"):
                qml_window.close()


def start_window_host(event_bus: EventBus) -> tuple[WindowHostController, StartupResult]:
    """Start the ui_api host bridge for runtime-owned windows."""

    controller = WindowHostController(event_bus)
    controller.attach()
    return controller, startup_ok()
