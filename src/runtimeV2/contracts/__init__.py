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

"""Public runtime V2 contracts used across domain boundaries."""

from runtimeV2.contracts.connectors import (
    ConnectorGameDetectorReader,
    ConnectorGameDetectorWriter,
    ConnectorReader,
    ConnectorWriter,
)
from runtimeV2.contracts.connectors_types import (
    ConnectorGameDetectedData,
    ConnectorGameLostData,
    ConnectorGameStateDecision,
    ConnectorGameStateUpdate,
    ConnectorInspectionSnapshot,
    ConnectorServiceRecord,
    ConnectorServiceRegisteredData,
    ConnectorServiceUnregisteredData,
    ConnectorServiceUpdatedData,
    ConnectorSourceChangedData,
)
from runtimeV2.contracts.events import EventRegistrationWriter, EventSubscriptionHandle
from runtimeV2.contracts.events_types import (
    Event,
    EventBus,
    EventCallback,
    EventType,
)
from runtimeV2.contracts.host import (
    AppIdentityReader,
    HostShellReader,
    MainWindowReader,
)
from runtimeV2.contracts.host_types import (
    HostAppIdentity,
    HostShell,
)
from runtimeV2.contracts.manifest import (
    ManifestConnectorReader,
    ManifestLoader,
    ManifestOverlayReader,
    ManifestReader,
    ManifestSettingsReader,
    ManifestUiReader,
)
from runtimeV2.contracts.paths_types import RuntimePaths
from runtimeV2.contracts.persistence import (
    SettingsReader,
    SettingsWriter,
    WidgetConfigReader,
    WidgetConfigWriter,
)
from runtimeV2.contracts.persistence_types import (
    BootstrapConfig,
    PersistencePaths,
    PersistenceStoreKind,
    PersistenceStoreRef,
    WidgetInstanceConfig,
)
from runtimeV2.contracts.plugins import (
    PluginActiveReader,
    PluginActiveWriter,
    PluginDiscovery,
    PluginIconResolver,
    PluginStateReader,
    PluginStateWriter,
)
from runtimeV2.contracts.plugins_types import PluginContext
from runtimeV2.contracts.runtime import RuntimeShutdownController
from runtimeV2.contracts.scheduler import SchedulerClockReader, SchedulerClockWriter, SchedulerWriter
from runtimeV2.contracts.scheduler_types import (
    ScheduledJobRecord,
    SchedulerClockMode,
    SchedulerClockState,
    SchedulerClockUpdatedData,
    SchedulerJobRegisteredData,
    SchedulerJobUpdatedData,
    SchedulerTickData,
)
from runtimeV2.contracts.ui import (
    UIChromeModelReader,
    PanelStateReader,
    PanelStateWriter,
    RenderStatusReader,
    WindowActionsWriter,
    WindowRecordsReader,
)
from runtimeV2.contracts.ui_types import (
    QmlPropertyPlan,
    UIChromeModel,
    UIMenuItem,
    UIPanelVisibilityChangedData,
    UIRenderStatus,
    UIStatusbarItem,
    UITabItem,
    UIWindowRecord,
    UIWindowRecordsChangedData,
    UIWindowStatus,
)
from runtimeV2.contracts.widgets import (
    WidgetManualOverrideState,
    WidgetRecordsReader,
    WidgetRecordsRefresher,
    WidgetTypeDefaultsReader,
    WidgetVisibilityReader,
    WidgetVisibilityWriter,
)
from runtimeV2.contracts.widgets_types import (
    WidgetRecord,
    WidgetRuntimeUpdatedData,
    WidgetStatus,
    WidgetVisibilityChangedData,
    WidgetVisibilityState,
)

__all__ = [
    # Connectors (capabilities)
    "ConnectorReader",
    "ConnectorWriter",
    "ConnectorGameDetectorReader",
    "ConnectorGameDetectorWriter",
    # Connectors (types)
    "ConnectorGameDetectedData",
    "ConnectorGameLostData",
    "ConnectorGameStateDecision",
    "ConnectorGameStateUpdate",
    "ConnectorInspectionSnapshot",
    "ConnectorServiceRecord",
    "ConnectorServiceRegisteredData",
    "ConnectorServiceUnregisteredData",
    "ConnectorServiceUpdatedData",
    "ConnectorSourceChangedData",
    # Events (capabilities)
    "EventRegistrationWriter",
    "EventSubscriptionHandle",
    # Events (types)
    "Event",
    "EventBus",
    "EventCallback",
    "EventType",
    # Host (capabilities)
    "MainWindowReader",
    "AppIdentityReader",
    "HostShellReader",
    # Host (types)
    "HostAppIdentity",
    "HostShell",
    # Manifest
    "ManifestReader",
    "ManifestLoader",
    "ManifestConnectorReader",
    "ManifestOverlayReader",
    "ManifestSettingsReader",
    "ManifestUiReader",
    # Paths (types)
    "RuntimePaths",
    # Persistence (capabilities)
    "SettingsReader",
    "SettingsWriter",
    "WidgetConfigReader",
    "WidgetConfigWriter",
    # Persistence (types)
    "BootstrapConfig",
    "PersistencePaths",
    "PersistenceStoreKind",
    "PersistenceStoreRef",
    "WidgetInstanceConfig",
    # Plugins (capabilities)
    "PluginDiscovery",
    "PluginActiveReader",
    "PluginActiveWriter",
    "PluginStateReader",
    "PluginStateWriter",
    "PluginIconResolver",
    # Plugins (types)
    "PluginContext",
    # Runtime (capabilities)
    "RuntimeShutdownController",
    # Scheduler (capabilities)
    "SchedulerClockReader",
    "SchedulerClockWriter",
    "SchedulerWriter",
    # Scheduler (types)
    "ScheduledJobRecord",
    "SchedulerClockMode",
    "SchedulerClockState",
    "SchedulerClockUpdatedData",
    "SchedulerJobRegisteredData",
    "SchedulerJobUpdatedData",
    "SchedulerTickData",
    # UI (capabilities)
    "UIChromeModelReader",
    "PanelStateReader",
    "PanelStateWriter",
    "RenderStatusReader",
    "WindowActionsWriter",
    "WindowRecordsReader",
    # UI (types)
    "QmlPropertyPlan",
    "UIChromeModel",
    "UIMenuItem",
    "UIPanelVisibilityChangedData",
    "UIRenderStatus",
    "UIStatusbarItem",
    "UITabItem",
    "UIWindowRecord",
    "UIWindowRecordsChangedData",
    "UIWindowStatus",
    # Widgets (capabilities)
    "WidgetManualOverrideState",
    "WidgetRecordsReader",
    "WidgetRecordsRefresher",
    "WidgetTypeDefaultsReader",
    "WidgetVisibilityReader",
    "WidgetVisibilityWriter",
    # Widgets (types)
    "WidgetRecord",
    "WidgetRuntimeUpdatedData",
    "WidgetStatus",
    "WidgetVisibilityChangedData",
    "WidgetVisibilityState",
]
