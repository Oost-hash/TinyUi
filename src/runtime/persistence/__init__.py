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

"""Persistence domain — manages configuration, settings, and widget state."""

from runtime.persistence.paths import ConfigResolver
from runtime.persistence.config_set import ConfigSet, ConfigSetManager
from runtime.persistence.registry import SettingsRegistry, ScopedSettings
from runtime.persistence.widget_config import (
    WidgetInstanceConfig,
    WidgetConfigStore,
)
from runtime.persistence.startup import (
    PersistenceStartupResult,
    startup_persistence,
    get_persistence_result,
)

__all__ = [
    # Core classes
    "ConfigResolver",
    "ConfigSet",
    "ConfigSetManager",
    "SettingsRegistry",
    "ScopedSettings",
    "WidgetInstanceConfig",
    "WidgetConfigStore",
    # Startup
    "PersistenceStartupResult",
    "startup_persistence",
    "get_persistence_result",
]
