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

"""widget_api host for runtime V2."""

from __future__ import annotations

from dataclasses import dataclass

from shared_runtime_host.capabilities.widget_host import WidgetHostCapability
from shared_runtime_host.registry import create_shared_runtime_host_registry
from shared_runtime_host.shutdown import QmlRuntimeHostShutdown
from runtimeV2.events.contracts import EventType
from runtimeV2.events.startup_shutdown.startup import EventsStartupResult
from runtimeV2.persistence.capabilities.widget_config_write import WidgetConfigWrite
from runtimeV2.runtime import RuntimeV2
from runtimeV2.schemas.startup import StartupResult, startup_error, startup_ok
from runtimeV2.widgets.startup_shutdown.startup import WidgetsStartupResult
from widget_api.register_runtime_host import register_widget_runtime_host
from widget_api.window_host import WidgetWindowHost


@dataclass(frozen=True)
class WidgetRuntimeHostResult:
    """Live widget_api objects hosting runtime V2 widget records."""

    controller: "WidgetWindowHostController"
    host: WidgetWindowHost
    shutdown: QmlRuntimeHostShutdown


class WidgetWindowHostController:
    """Keep the widget window host synchronized with runtime changes."""

    def __init__(self, runtime: RuntimeV2, host: WidgetWindowHost) -> None:
        self._runtime = runtime
        self._events = runtime.domain_result("events", EventsStartupResult)
        self._widgets = runtime.domain_result("widgets", WidgetsStartupResult)
        self._host = host

    def attach(self, app) -> None:
        """Subscribe to runtime V2 events that change widget runtime records."""

        for event_type in (
            EventType.PLUGIN_STATE_CHANGED,
            EventType.PLUGIN_ERROR,
            EventType.CONNECTOR_SERVICE_REGISTERED,
            EventType.CONNECTOR_SERVICE_UNREGISTERED,
            EventType.CONNECTOR_SERVICE_UPDATED,
            EventType.WIDGET_RUNTIME_UPDATED,
        ):
            self._events.bus.on(event_type, self._on_runtime_change)

    def sync(self) -> None:
        """Refresh hosted windows from current widget runtime records."""

        self._host.sync_records(self._widgets.store.all_widget_records())

    def refresh(self) -> None:
        """Refresh widgets through the widgets domain and sync the host."""

        self._widgets.poller.refresh()
        self.sync()

    def _on_runtime_change(self, event) -> None:
        if event.type != EventType.WIDGET_RUNTIME_UPDATED:
            self._widgets.poller.refresh()
        self.sync()


def create_widget_window_host(app, runtime: RuntimeV2) -> WidgetRuntimeHostResult:
    """Create the widget_api host bridge for runtime V2 widget records."""

    host_registry = create_shared_runtime_host_registry(runtime)
    register_widget_runtime_host(host_registry)
    widget_host = host_registry.capability("widget_host", WidgetHostCapability)
    host = WidgetWindowHost(widget_host, runtime.capability("widget_config_write", WidgetConfigWrite))
    controller = WidgetWindowHostController(runtime, host)
    controller.sync()
    controller.attach(app)
    shutdown = QmlRuntimeHostShutdown(runtime, host.close_all)
    shutdown.attach(app)
    result = WidgetRuntimeHostResult(controller=controller, host=host, shutdown=shutdown)
    app.setProperty("_widgetRuntimeHost", result)
    return result


def start_widget_host(app, runtime: RuntimeV2) -> tuple[WidgetRuntimeHostResult | None, StartupResult]:
    """Start the widget_api host bridge for runtime V2 widget records."""

    try:
        return create_widget_window_host(app, runtime), startup_ok()
    except Exception as exc:
        return None, startup_error(f"widget_api runtime host startup failed: {exc}")

