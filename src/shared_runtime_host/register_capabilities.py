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

"""Register shared runtime host projection capabilities."""

from __future__ import annotations

from runtimeV2.contracts import (
    ConfigSetReader,
    ConfigSetWriter,
    ConnectorWriter,
    EventRegistrationWriter,
    ManifestConnectorReader,
    PanelStateWriter,
    PluginActiveWriter,
    PluginDiscovery,
    SettingsWriter,
    UIChromeModelReader,
    WidgetRecordsReader,
    WidgetVisibilityReader,
    WidgetVisibilityWriter,
    WindowActionsWriter,
    WindowRecordsReader,
)
from runtimeV2.scheduler.capabilities.scheduler_write import SchedulerWrite
from runtimeV2.widgets.capabilities.widget_manual_override import WidgetManualOverride
from runtimeV2.widgets.capabilities.widget_manual_override import WidgetManualOverride
from runtimeV2.capabilities.runtime_shutdown import RuntimeShutdown
from shared_runtime_host.capabilities.ui_api import UIActionsCapability
from shared_runtime_host.capabilities.widget_api import WidgetEffectsQmlCapability
from shared_runtime_host.capabilities.ui_host import UIHostCapability
from shared_runtime_host.capabilities.window_host import WindowHostCapability
from shared_runtime_host.capabilities.widget_host import WidgetHostCapability
from shared_runtime_host.events import SharedRuntimeHostEvents
from shared_runtime_host.registry import SharedRuntimeHostRegistry


def register_event_registration_host(registry: SharedRuntimeHostRegistry) -> None:
    """Register the shared host event registration bridge."""

    runtime = registry.runtime
    registry.register_capability(
        "event_registration",
        SharedRuntimeHostEvents(runtime.capability("event_registration_write", EventRegistrationWriter)),
    )


def register_widget_host(registry: SharedRuntimeHostRegistry) -> None:
    """Register the shared widget host projection."""

    runtime = registry.runtime
    registry.register_capability(
        "widget_host",
        WidgetHostCapability(runtime.capability("widget_records_read", WidgetRecordsReader)),
    )


def register_widget_effects_host(registry: SharedRuntimeHostRegistry) -> None:
    """Register the shared widget effects projection."""

    runtime = registry.runtime
    registry.register_capability(
        "widget_effects",
        WidgetEffectsQmlCapability(runtime.capability("scheduler_write", SchedulerWrite)),
    )


def register_ui_host(registry: SharedRuntimeHostRegistry) -> None:
    """Register the shared UI chrome projection."""

    runtime = registry.runtime
    registry.register_capability(
        "ui_host",
        UIHostCapability(runtime.capability("ui_chrome_model_read", UIChromeModelReader)),
    )


def register_window_host(registry: SharedRuntimeHostRegistry) -> None:
    """Register the shared window record projection."""

    runtime = registry.runtime
    registry.register_capability(
        "window_host",
        WindowHostCapability(runtime.capability("window_records_read", WindowRecordsReader)),
    )


def register_ui_actions_host(registry: SharedRuntimeHostRegistry) -> None:
    """Register the shared ui_api action projection."""

    runtime = registry.runtime
    registry.register_capability(
        "ui_actions",
        UIActionsCapability(
            window_actions=runtime.capability("window_actions_write", WindowActionsWriter),
            manifest_connector_read=runtime.capability("manifest_connector_read", ManifestConnectorReader),
            connector_write=runtime.capability("connector_write", ConnectorWriter),
            widget_visibility_read=runtime.capability("widget_visibility_read", WidgetVisibilityReader),
            widget_visibility_write=runtime.capability("widget_visibility_write", WidgetVisibilityWriter),
            widget_manual_override=runtime.capability("widget_manual_override", WidgetManualOverride),
            plugin_discovery=runtime.capability("plugin_discovery", PluginDiscovery),
            plugin_active_write=runtime.capability("plugin_active_write", PluginActiveWriter),
            config_set_read=runtime.capability("config_set_read", ConfigSetReader),
            config_set_write=runtime.capability("config_set_write", ConfigSetWriter),
            settings_write=runtime.capability("settings_write", SettingsWriter),
            panel_state_write=runtime.capability("panel_state_write", PanelStateWriter),
            shutdown=runtime.capability("shutdown", RuntimeShutdown),
        ),
    )
