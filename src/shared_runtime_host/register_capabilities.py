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

from runtimeV2.ui.capabilities.chrome_model_read import UIChromeModelRead
from runtimeV2.ui.capabilities.window_actions_write import WindowActionsWrite
from runtimeV2.connectors.capabilities.connector_write import ConnectorWrite
from runtimeV2.manifest.capabilities.connector_read import ManifestConnectorRead
from runtimeV2.ui.capabilities.window_records_read import WindowRecordsRead
from runtimeV2.persistence.capabilities.config_set_read import ConfigSetRead
from runtimeV2.persistence.capabilities.config_set_write import ConfigSetWrite
from runtimeV2.persistence.capabilities.settings_write import SettingsWrite
from runtimeV2.plugins.capabilities.active_write import PluginActiveWrite
from runtimeV2.plugins.capabilities.discovery import PluginDiscoveryCapability
from runtimeV2.scheduler.capabilities.scheduler_write import SchedulerWrite
from runtimeV2.ui.capabilities.panel_state_write import PanelStateWrite
from runtimeV2.contracts.widgets import WidgetRecordsReader
from runtimeV2.widgets.capabilities.widget_manual_override import WidgetManualOverride
from runtimeV2.widgets.capabilities.widget_visibility_read import WidgetVisibilityRead
from runtimeV2.widgets.capabilities.widget_visibility_write import WidgetVisibilityWrite
from runtimeV2.capabilities.runtime_shutdown import RuntimeShutdown
from runtimeV2.events.capabilities.event_registration_write import EventRegistrationWrite

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
        SharedRuntimeHostEvents(runtime.capability("event_registration_write", EventRegistrationWrite)),
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
        UIHostCapability(runtime.capability("ui_chrome_model_read", UIChromeModelRead)),
    )


def register_window_host(registry: SharedRuntimeHostRegistry) -> None:
    """Register the shared window record projection."""

    runtime = registry.runtime
    registry.register_capability(
        "window_host",
        WindowHostCapability(runtime.capability("window_records_read", WindowRecordsRead)),
    )


def register_ui_actions_host(registry: SharedRuntimeHostRegistry) -> None:
    """Register the shared ui_api action projection."""

    runtime = registry.runtime
    registry.register_capability(
        "ui_actions",
        UIActionsCapability(
            window_actions=runtime.capability("window_actions_write", WindowActionsWrite),
            manifest_connector_read=runtime.capability("manifest_connector_read", ManifestConnectorRead),
            connector_write=runtime.capability("connector_write", ConnectorWrite),
            widget_visibility_read=runtime.capability("widget_visibility_read", WidgetVisibilityRead),
            widget_visibility_write=runtime.capability("widget_visibility_write", WidgetVisibilityWrite),
            widget_manual_override=runtime.capability("widget_manual_override", WidgetManualOverride),
            plugin_discovery=runtime.capability("plugin_discovery", PluginDiscoveryCapability),
            plugin_active_write=runtime.capability("plugin_active_write", PluginActiveWrite),
            config_set_read=runtime.capability("config_set_read", ConfigSetRead),
            config_set_write=runtime.capability("config_set_write", ConfigSetWrite),
            settings_write=runtime.capability("settings_write", SettingsWrite),
            panel_state_write=runtime.capability("panel_state_write", PanelStateWrite),
            shutdown=runtime.capability("shutdown", RuntimeShutdown),
        ),
    )
