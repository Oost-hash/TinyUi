"""Register shared runtime host projection capabilities."""

from __future__ import annotations

from runtimeV2.ui.capabilities.chrome_model_read import UIChromeModelRead
from runtimeV2.ui.capabilities.window_actions_write import WindowActionsWrite
from runtimeV2.ui.capabilities.window_records_read import WindowRecordsRead
from runtimeV2.persistence.capabilities.config_set_read import ConfigSetRead
from runtimeV2.persistence.capabilities.config_set_write import ConfigSetWrite
from runtimeV2.persistence.capabilities.settings_write import SettingsWrite
from runtimeV2.plugins.capabilities.active_write import PluginActiveWrite
from runtimeV2.plugins.capabilities.discovery import PluginDiscoveryCapability
from runtimeV2.widgets.capabilities.widget_visibility_read import WidgetVisibilityRead
from runtimeV2.widgets.capabilities.widget_visibility_write import WidgetVisibilityWrite
from runtimeV2.capabilities.runtime_shutdown import RuntimeShutdown
from runtimeV2.widgets.capabilities.widget_records_read import WidgetRecordsRead

from shared_runtime_host.capabilities.ui_api import UIActionsCapability
from shared_runtime_host.capabilities.ui_host import UIHostCapability
from shared_runtime_host.capabilities.window_host import WindowHostCapability
from shared_runtime_host.capabilities.widget_host import WidgetHostCapability
from shared_runtime_host.registry import SharedRuntimeHostRegistry


def register_widget_host(registry: SharedRuntimeHostRegistry) -> None:
    """Register the shared widget host projection."""

    runtime = registry.runtime
    registry.register_capability(
        "widget_host",
        WidgetHostCapability(runtime.capability("widget_records_read", WidgetRecordsRead)),
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
            widget_visibility_read=runtime.capability("widget_visibility_read", WidgetVisibilityRead),
            widget_visibility_write=runtime.capability("widget_visibility_write", WidgetVisibilityWrite),
            plugin_discovery=runtime.capability("plugin_discovery", PluginDiscoveryCapability),
            plugin_active_write=runtime.capability("plugin_active_write", PluginActiveWrite),
            config_set_read=runtime.capability("config_set_read", ConfigSetRead),
            config_set_write=runtime.capability("config_set_write", ConfigSetWrite),
            settings_write=runtime.capability("settings_write", SettingsWrite),
            shutdown=runtime.capability("shutdown", RuntimeShutdown),
        ),
    )
