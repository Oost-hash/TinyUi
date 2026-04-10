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

from shared_runtime_host.events import SharedRuntimeHostEvents
from shared_runtime_host.capabilities.widget_api import WidgetEffectsQmlCapability
from shared_runtime_host.capabilities.widget_host import WidgetHostCapability
from shared_runtime_host.registry import SharedRuntimeHostRegistry
from shared_runtime_host.shutdown import QmlRuntimeHostShutdown
from runtimeV2.events.contracts import EventType
from runtimeV2.persistence.capabilities.widget_config_write import WidgetConfigWrite
from runtimeV2.runtime import RuntimeV2
from runtimeV2.schemas.startup import StartupResult, startup_error, startup_ok
from widget_api.window_host import WidgetWindowHost


@dataclass(frozen=True)
class WidgetRuntimeHostResult:
    """Live widget_api objects hosting runtime V2 widget records."""

    controller: "WidgetWindowHostController"
    host: WidgetWindowHost
    shutdown: QmlRuntimeHostShutdown


class WidgetWindowHostController:
    """Keep the widget window host synchronized with runtime changes."""

    def __init__(
        self,
        *,
        widget_host: WidgetHostCapability,
        event_registration: SharedRuntimeHostEvents,
        host: WidgetWindowHost,
    ) -> None:
        self._widget_host = widget_host
        self._event_registration = event_registration
        self._host = host

    def attach(self, app) -> None:
        """Subscribe to runtime V2 events that change widget runtime records."""

        self._event_registration.subscribe(
            owner_domain="widget_api",
            event_type=EventType.WIDGET_RUNTIME_UPDATED,
            callback=self._on_widgets_updated,
            description="Sync hosted widget windows with runtime widget changes.",
        )

    def sync(self) -> None:
        """Refresh hosted windows from current widget runtime records."""

        self._host.sync_records(self._widget_host.records())

    def _on_widgets_updated(self, _event) -> None:
        self.sync()


def create_widget_window_host(
    app,
    runtime: RuntimeV2,
    host_registry: SharedRuntimeHostRegistry,
) -> WidgetRuntimeHostResult:
    """Create the widget_api host bridge for runtime V2 widget records."""

    widget_host = host_registry.capability("widget_host", WidgetHostCapability)
    widget_effects = host_registry.capability("widget_effects", WidgetEffectsQmlCapability)
    event_registration = host_registry.capability("event_registration", SharedRuntimeHostEvents)
    host = WidgetWindowHost(
        widget_host,
        runtime.capability("widget_config_write", WidgetConfigWrite),
        widget_effects,
    )
    controller = WidgetWindowHostController(
        widget_host=widget_host,
        event_registration=event_registration,
        host=host,
    )
    controller.sync()
    controller.attach(app)
    shutdown = QmlRuntimeHostShutdown(runtime, host.close_all)
    shutdown.attach(app)
    result = WidgetRuntimeHostResult(controller=controller, host=host, shutdown=shutdown)
    app.setProperty("_widgetRuntimeHost", result)
    return result


def start_widget_host(
    app,
    runtime: RuntimeV2,
    host_registry: SharedRuntimeHostRegistry,
) -> tuple[WidgetRuntimeHostResult | None, StartupResult]:
    """Start the widget_api host bridge for runtime V2 widget records."""

    try:
        return create_widget_window_host(app, runtime, host_registry), startup_ok()
    except Exception as exc:
        return None, startup_error(f"widget_api runtime host startup failed: {exc}")

