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

"""Startup for runtime V2 persistence."""

from __future__ import annotations

from dataclasses import dataclass

from runtime_schema import StartupResult, startup_error, startup_ok
from runtimeV2.host.capabilities.app_identity_read import AppIdentityRead
from runtimeV2.persistence.config_sets import ConfigSetCatalog
from runtimeV2.persistence.contracts import PersistencePaths
from runtimeV2.persistence.paths import resolve_persistence_paths
from runtimeV2.persistence.register_capabilities import (
    PersistenceCapabilities,
    register_persistence_capabilities,
)
from runtimeV2.persistence.register_paths import register_persistence_paths
from runtimeV2.persistence.register_settings import register_settings_specs
from runtimeV2.persistence.settings import SettingsStore
from runtimeV2.persistence.widget_config import WidgetConfigStore
from runtimeV2.plugins.capabilities.settings_spec_read import PluginSettingsSpecRead
from runtimeV2.runtime import RuntimeV2


@dataclass(frozen=True)
class PersistenceStartupResult:
    """Result of persistence domain startup."""

    paths: PersistencePaths
    catalog: ConfigSetCatalog
    settings: SettingsStore
    widget_config: WidgetConfigStore
    capabilities: PersistenceCapabilities


def startup_persistence(runtime: RuntimeV2) -> StartupResult:
    """Start runtime V2 persistence."""

    try:
        identity_read = runtime.capability("app_identity_read", AppIdentityRead)
        settings_spec_read = runtime.capability("plugin_settings_spec_read", PluginSettingsSpecRead)
        paths = register_persistence_paths(resolve_persistence_paths(identity_read))
        catalog = ConfigSetCatalog(paths)
        active_set = catalog.active_set().id
        settings = SettingsStore(paths, active_set)
        register_settings_specs(settings=settings, settings_spec_read=settings_spec_read)
        widget_config = WidgetConfigStore(paths, active_set)
        capabilities = register_persistence_capabilities(
            catalog=catalog,
            settings=settings,
            widget_config=widget_config,
        )
        runtime.register_capability("config_set_read", capabilities.config_set_read)
        runtime.register_capability("config_set_write", capabilities.config_set_write)
        runtime.register_capability("settings_read", capabilities.settings_read)
        runtime.register_capability("settings_write", capabilities.settings_write)
        runtime.register_capability("widget_config_read", capabilities.widget_config_read)
        runtime.register_capability("widget_config_write", capabilities.widget_config_write)
        runtime.register_domain_result("persistence", PersistenceStartupResult(
            paths=paths,
            catalog=catalog,
            settings=settings,
            widget_config=widget_config,
            capabilities=capabilities,
        ))
        return startup_ok()
    except Exception as exc:
        return startup_error(f"Persistence domain startup failed: {exc}")
