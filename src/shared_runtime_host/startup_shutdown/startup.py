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

"""Shared runtime host bridge startup."""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtQml import QQmlEngine
from PySide6.QtWidgets import QApplication

from runtimeV2.runtime import RuntimeV2
from runtimeV2.schemas.startup import StartupResult, startup_error, startup_ok
from shared_runtime_host.register_capabilities import register_event_registration_host, register_widget_host
from shared_runtime_host.registry import SharedRuntimeHostRegistry, create_shared_runtime_host_registry
from shared_runtime_host.scheduler import QmlRuntimeSchedulerDriver, start_runtime_scheduler_clock
from ui_api.register_runtime_host import register_ui_runtime_host
from ui_api.runtime_host import RuntimeHostResult, start_runtime_host
from ui_api.startup_logging import log_startup_step
from widget_api.register_runtime_host import register_widget_runtime_host
from widget_api.runtime_host import WidgetRuntimeHostResult
from widget_api.startup_shutdown.startup import startup_widget_api


@dataclass(frozen=True)
class SharedRuntimeHostStartupResult:
    """Live host bridge objects above runtime V2."""

    registry: SharedRuntimeHostRegistry
    scheduler_driver: QmlRuntimeSchedulerDriver
    ui_host: RuntimeHostResult
    widget_host: WidgetRuntimeHostResult


def _stop_scheduler_driver(driver: QmlRuntimeSchedulerDriver | None) -> None:
    if driver is None or not hasattr(driver, "stop"):
        return
    driver.stop()


def startup_shared_runtime_host(
    app: QApplication,
    engine: QQmlEngine,
    runtime: RuntimeV2,
) -> tuple[SharedRuntimeHostStartupResult | None, StartupResult]:
    """Start shared host bridge and API hosts above runtime V2."""

    scheduler_driver: QmlRuntimeSchedulerDriver | None = None
    ui_host: RuntimeHostResult | None = None
    widget_host: WidgetRuntimeHostResult | None = None

    try:
        log_startup_step("shared runtime host startup begin")
        registry = create_shared_runtime_host_registry(runtime)
        register_event_registration_host(registry)
        register_widget_host(registry)
        register_ui_runtime_host(registry)
        register_widget_runtime_host(registry)

        scheduler_driver = start_runtime_scheduler_clock(app, runtime)

        ui_host, ui_result = start_runtime_host(
            app=app,
            engine=engine,
            runtime=runtime,
            host_registry=registry,
        )
        if not ui_result.ok or ui_host is None:
            _stop_scheduler_driver(scheduler_driver)
            return None, startup_error(ui_result.error_message or "ui_api host startup failed")

        widget_host, widget_result = startup_widget_api(
            app=app,
            runtime=runtime,
            host_registry=registry,
        )
        if not widget_result.ok or widget_host is None:
            ui_host.shutdown.close_host()
            _stop_scheduler_driver(scheduler_driver)
            return None, startup_error(widget_result.error_message or "widget_api host startup failed")

        result = SharedRuntimeHostStartupResult(
            registry=registry,
            scheduler_driver=scheduler_driver,
            ui_host=ui_host,
            widget_host=widget_host,
        )
        app.setProperty("_sharedRuntimeHost", result)
        log_startup_step("shared runtime host startup completed")
        return result, startup_ok()
    except Exception as exc:
        if widget_host is not None:
            widget_host.shutdown.close_host()
        if ui_host is not None:
            ui_host.shutdown.close_host()
        _stop_scheduler_driver(scheduler_driver)
        log_startup_step(f"shared runtime host startup exception: {exc}", level=40, exc_info=True)
        return None, startup_error(f"Shared runtime host startup failed: {exc}")
