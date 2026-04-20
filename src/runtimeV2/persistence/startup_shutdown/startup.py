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

from runtimeV2.contracts import AppIdentityReader, ManifestSettingsReader
from runtimeV2.persistence.backends import PersistenceBackend
from runtimeV2.persistence.bootstrap import load_bootstrap
from runtimeV2.persistence.contracts import BootstrapConfig, PersistencePaths
from runtimeV2.persistence.overlay_content import HostPluginStyleStore, OverlayLayoutStore, OverlayThemeStore
from runtimeV2.persistence.overlay_index import OverlayIndexStore
from runtimeV2.persistence.paths import resolve_persistence_paths
from runtimeV2.persistence.registry import PersistenceRegistry
from runtimeV2.persistence.repository import PersistenceRepository
from runtimeV2.persistence.reset_service import PersistenceResetService
from runtimeV2.persistence.settings import SettingsStore
from runtimeV2.persistence.startup_shutdown.register_capabilities import (
    PersistenceCapabilities,
    register_persistence_capabilities,
)
from runtimeV2.persistence.startup_shutdown.register_paths import register_persistence_paths
from runtimeV2.persistence.startup_shutdown.register_persistence import register_persistence_document_schemas
from runtimeV2.persistence.startup_shutdown.register_settings import register_settings_specs
from runtimeV2.persistence.store_provider import PersistenceStoreProvider
from runtimeV2.persistence.widget_config import WidgetConfigStore
from runtimeV2.runtime import RuntimeV2
from runtimeV2.schemas.startup import StartupResult, startup_error, startup_ok


@dataclass(frozen=True)
class PersistenceStartupResult:
    """Result of persistence startup."""

    config: BootstrapConfig
    paths: PersistencePaths
    app_backend: PersistenceBackend
    registry: PersistenceRegistry
    repository: PersistenceRepository
    store_provider: PersistenceStoreProvider
    overlay_index: OverlayIndexStore
    overlay_theme: OverlayThemeStore
    overlay_layout: OverlayLayoutStore
    host_plugin_style: HostPluginStyleStore
    reset_service: PersistenceResetService
    settings: SettingsStore
    widget_config: WidgetConfigStore
    capabilities: PersistenceCapabilities


def startup_persistence(runtime: RuntimeV2) -> StartupResult:
    """Start the persistence domain."""

    try:
        identity_read = runtime.capability("app_identity_read", AppIdentityReader)
        manifest_settings_read = runtime.capability("manifest_settings_read", ManifestSettingsReader)
        paths = register_persistence_paths(resolve_persistence_paths(identity_read))
        config = load_bootstrap(paths.bootstrap_path)
        registry = PersistenceRegistry()
        register_persistence_document_schemas(registry)
        store_provider = PersistenceStoreProvider(
            config=config,
            paths=paths,
            registry=registry,
        )
        repository = store_provider.app_repository()
        overlay_index = OverlayIndexStore(repository)
        settings = SettingsStore(repository)
        register_settings_specs(settings, manifest_settings_read)
        widget_config = WidgetConfigStore(
            repository,
            overlay_repository=store_provider.overlay_repository,
            overlay_index=overlay_index,
        )
        overlay_theme = OverlayThemeStore(
            overlay_index=overlay_index,
            overlay_repository=store_provider.overlay_repository,
        )
        overlay_layout = OverlayLayoutStore(
            overlay_index=overlay_index,
            overlay_repository=store_provider.overlay_repository,
        )
        host_plugin_style = HostPluginStyleStore(
            overlay_index=overlay_index,
            overlay_repository=store_provider.overlay_repository,
        )
        reset_service = PersistenceResetService(
            overlay_index=overlay_index,
            store_provider=store_provider,
            widget_config=widget_config,
        )
        capabilities = register_persistence_capabilities(
            settings=settings,
            widget_config=widget_config,
        )
        runtime.register_capability("settings_read", capabilities.settings_read)
        runtime.register_capability("settings_write", capabilities.settings_write)
        runtime.register_capability("widget_config_read", capabilities.widget_config_read)
        runtime.register_capability("widget_config_write", capabilities.widget_config_write)
        runtime.register_stop_hook("persistence", store_provider.close)
        runtime.register_domain_result("persistence", PersistenceStartupResult(
            config=config,
            paths=paths,
            app_backend=store_provider.app_backend(),
            registry=registry,
            repository=repository,
            store_provider=store_provider,
            overlay_index=overlay_index,
            overlay_theme=overlay_theme,
            overlay_layout=overlay_layout,
            host_plugin_style=host_plugin_style,
            reset_service=reset_service,
            settings=settings,
            widget_config=widget_config,
            capabilities=capabilities,
        ))
        return startup_ok()
    except Exception as exc:
        return startup_error(f"Persistence domain startup failed: {exc}")
