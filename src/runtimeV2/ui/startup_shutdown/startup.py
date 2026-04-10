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

"""Startup for runtime V2 UI."""

from __future__ import annotations

from dataclasses import dataclass

from runtimeV2.capabilities.runtime_globals import RuntimeGlobals
from runtimeV2.events.contracts import Event, EventType
from runtimeV2.events.startup_shutdown.startup import EventsStartupResult
from runtimeV2.host.capabilities.main_window_read import MainWindowRead
from runtimeV2.manifest.capabilities.ui_read import ManifestUiRead
from runtimeV2.plugins.capabilities.active_read import PluginActiveRead
from runtimeV2.runtime import RuntimeV2
from runtimeV2.ui.chrome_model import build_ui_chrome_model
from runtimeV2.contracts import (
    QmlPropertyPlan,
    UIChromeModel,
    UIRenderStatus,
    UIWindowRecord,
    UIWindowRecordsChangedData,
)
from runtimeV2.ui.projection import project_ui_window_records
from runtimeV2.ui.readiness import determine_render_status
from runtimeV2.ui.startup_shutdown.register_capabilities import UICapabilities, register_ui_capabilities
from runtimeV2.ui.startup_shutdown.register_events import register_ui_events
from runtimeV2.ui.startup_shutdown.register_qml_properties import register_qml_property_plan
from runtimeV2.ui.panel_state import UIPanelStateStore
from runtimeV2.schemas.startup import StartupResult, startup_error, startup_ok


@dataclass(frozen=True)
class UIStartupResult:
    """Result of UI domain startup."""

    records: list[UIWindowRecord]
    render_status: UIRenderStatus
    chrome_model: UIChromeModel
    qml_property_plan: list[QmlPropertyPlan]
    capabilities: UICapabilities


def startup_ui(runtime: RuntimeV2) -> StartupResult:
    """Start runtime V2 UI read-models and handoff data."""

    try:
        events = runtime.domain_result("events", EventsStartupResult)
        register_ui_events(events.registry)
        main_window_read = runtime.capability("main_window_read", MainWindowRead)
        records = project_ui_window_records(
            ui_manifest_read=runtime.capability("manifest_ui_read", ManifestUiRead),
            main_window_read=main_window_read,
        )
        render_status = determine_render_status(
            main_window_read=main_window_read,
            records=records,
        )
        globals_capability = runtime.capability("globals", RuntimeGlobals)
        chrome_model = build_ui_chrome_model(
            main_window_read=main_window_read,
            ui_manifest_read=runtime.capability("manifest_ui_read", ManifestUiRead),
            active_read=globals_capability.read_global("active_plugin", PluginActiveRead),
        )
        panel_state = UIPanelStateStore(events)
        qml_property_plan = register_qml_property_plan()
        capabilities = register_ui_capabilities(
            records=records,
            main_window_id=main_window_read.main_window().id,
            panel_state=panel_state,
            render_status=render_status,
            chrome_model=chrome_model,
        )
        runtime.register_capability("window_records_read", capabilities.window_records_read)
        runtime.register_capability("window_actions_write", capabilities.window_actions_write)
        runtime.register_capability("panel_state_read", capabilities.panel_state_read)
        runtime.register_capability("panel_state_write", capabilities.panel_state_write)
        runtime.register_capability("render_status_read", capabilities.render_status_read)
        runtime.register_capability("ui_chrome_model_read", capabilities.chrome_model_read)
        runtime.register_domain_result("ui", UIStartupResult(
            records=records,
            render_status=render_status,
            chrome_model=chrome_model,
            qml_property_plan=qml_property_plan,
            capabilities=capabilities,
        ))
        events.bus.emit_typed(
            EventType.UI_WINDOW_RECORDS_CHANGED,
            UIWindowRecordsChangedData(window_count=len(records)),
            source="ui",
        )
        event_type = EventType.UI_READY if render_status.render_ready else EventType.UI_RENDER_BLOCKED
        events.bus.emit(Event(event_type, data=render_status, source="ui"))
        return startup_ok()
    except Exception as exc:
        return startup_error(f"UI domain startup failed: {exc}")

