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

"""Capability registration for runtime V2 persistence."""

from __future__ import annotations

from dataclasses import dataclass

from runtimeV2.persistence.capabilities.config_set_read import ConfigSetRead
from runtimeV2.persistence.capabilities.config_set_write import ConfigSetWrite
from runtimeV2.persistence.capabilities.settings_read import SettingsRead
from runtimeV2.persistence.capabilities.settings_write import SettingsWrite
from runtimeV2.persistence.capabilities.widget_config_read import WidgetConfigRead
from runtimeV2.persistence.capabilities.widget_config_write import WidgetConfigWrite
from runtimeV2.persistence.config_sets import ConfigSetCatalog
from runtimeV2.persistence.settings import SettingsStore
from runtimeV2.persistence.widget_config import WidgetConfigStore


@dataclass(frozen=True)
class PersistenceCapabilities:
    """Capabilities exposed by the persistence domain."""

    config_set_read: ConfigSetRead
    config_set_write: ConfigSetWrite
    settings_read: SettingsRead
    settings_write: SettingsWrite
    widget_config_read: WidgetConfigRead
    widget_config_write: WidgetConfigWrite


def register_persistence_capabilities(
    *,
    catalog: ConfigSetCatalog,
    settings: SettingsStore,
    widget_config: WidgetConfigStore,
) -> PersistenceCapabilities:
    """Create persistence domain capabilities."""

    return PersistenceCapabilities(
        config_set_read=ConfigSetRead(catalog),
        config_set_write=ConfigSetWrite(catalog),
        settings_read=SettingsRead(settings),
        settings_write=SettingsWrite(settings),
        widget_config_read=WidgetConfigRead(widget_config),
        widget_config_write=WidgetConfigWrite(widget_config),
    )
