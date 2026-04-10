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
from runtimeV2.contracts.events import EventRegistrationWriter, EventSubscriptionHandle
from runtimeV2.contracts.host import (
    AppIdentityReader,
    HostShellReader,
    MainWindowReader,
)
from runtimeV2.contracts.manifest import (
    ManifestConnectorReader,
    ManifestLoader,
    ManifestOverlayReader,
    ManifestReader,
    ManifestSettingsReader,
    ManifestUiReader,
)
from runtimeV2.contracts.persistence import (
    ConfigSetReader,
    ConfigSetWriter,
    SettingsReader,
    SettingsWriter,
    WidgetConfigReader,
    WidgetConfigWriter,
)
from runtimeV2.contracts.plugins import (
    PluginActiveReader,
    PluginActiveWriter,
    PluginDiscovery,
    PluginIconResolver,
    PluginStateReader,
    PluginStateWriter,
)
from runtimeV2.contracts.scheduler import SchedulerClockReader
from runtimeV2.contracts.ui import (
    UIChromeModelReader,
    PanelStateReader,
    PanelStateWriter,
    WindowActionsWriter,
    WindowRecordsReader,
)
from runtimeV2.contracts.widgets import (
    WidgetRecordsReader,
    WidgetVisibilityReader,
    WidgetVisibilityWriter,
)

__all__ = [
    # Connectors
    "ConnectorReader",
    "ConnectorWriter",
    "ConnectorGameDetectorReader",
    "ConnectorGameDetectorWriter",
    # Events
    "EventRegistrationWriter",
    "EventSubscriptionHandle",
    # Host
    "MainWindowReader",
    "AppIdentityReader",
    "HostShellReader",
    # Manifest
    "ManifestReader",
    "ManifestLoader",
    "ManifestConnectorReader",
    "ManifestOverlayReader",
    "ManifestSettingsReader",
    "ManifestUiReader",
    # Persistence
    "SettingsReader",
    "SettingsWriter",
    "WidgetConfigReader",
    "WidgetConfigWriter",
    "ConfigSetReader",
    "ConfigSetWriter",
    # Plugins
    "PluginDiscovery",
    "PluginActiveReader",
    "PluginActiveWriter",
    "PluginStateReader",
    "PluginStateWriter",
    "PluginIconResolver",
    # Scheduler
    "SchedulerClockReader",
    # UI
    "UIChromeModelReader",
    "PanelStateReader",
    "PanelStateWriter",
    "WindowActionsWriter",
    "WindowRecordsReader",
    # Widgets
    "WidgetRecordsReader",
    "WidgetVisibilityReader",
    "WidgetVisibilityWriter",
]
