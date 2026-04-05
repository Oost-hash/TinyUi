"""Qt host bridge for runtime-owned widget records."""

from __future__ import annotations

from typing import Protocol, Sequence

from runtime_schema import EventBus, EventType
from runtime.widgets import WidgetRuntimePoller, WidgetRuntimeRecord
from widget_api.window_host import WidgetWindowHost


class WidgetRuntimeLike(Protocol):
    """Minimal runtime surface needed by the widget host bridge."""

    def active_overlay_widget_records(self) -> Sequence[WidgetRuntimeRecord]: ...


class WidgetWindowHostController:
    """Keep the widget window host synchronized with runtime changes."""

    def __init__(self, event_bus: EventBus, runtime: WidgetRuntimeLike, host: WidgetWindowHost) -> None:
        self._event_bus = event_bus
        self._runtime = runtime
        self._host = host

    def attach(self) -> None:
        """Subscribe to the runtime events that can change active widget records."""

        for event_type in (
            EventType.PLUGIN_STATE_CHANGED,
            EventType.PLUGIN_ERROR,
            EventType.UI_PLUGIN_SELECTED,
            EventType.CONNECTOR_SERVICE_REGISTERED,
            EventType.CONNECTOR_SERVICE_UNREGISTERED,
            EventType.CONNECTOR_SERVICE_UPDATED,
            EventType.RUNTIME_SHUTDOWN,
            EventType.WIDGET_RUNTIME_UPDATED,
        ):
            self._event_bus.on(event_type, self._on_runtime_change)

    def sync(self) -> None:
        """Refresh hosted windows from current runtime widget records."""

        self._host.sync_records(self._runtime.active_overlay_widget_records())

    def _on_runtime_change(self, _event) -> None:
        self.sync()


def create_widget_window_host(app, event_bus: EventBus, runtime: WidgetRuntimeLike) -> WidgetWindowHost:
    """Create the widget window host and keep it synchronized with runtime records."""

    host = WidgetWindowHost()
    controller = WidgetWindowHostController(event_bus, runtime, host)
    poller = WidgetRuntimePoller(event_bus)
    controller.sync()
    controller.attach()
    poller.start()
    app.aboutToQuit.connect(host.close_all)
    app.aboutToQuit.connect(poller.stop)
    app.setProperty("_widgetWindowHostController", controller)
    app.setProperty("_widgetRuntimePoller", poller)
    return host
