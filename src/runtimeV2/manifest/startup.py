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

"""Startup for runtime V2 manifest."""

from __future__ import annotations

from dataclasses import dataclass

from runtimeV2.schemas.startup import StartupResult, startup_error, startup_ok
from runtimeV2.manifest.register_capabilities import ManifestCapabilities, register_manifest_capabilities
from runtimeV2.manifest.register_schemas import register_manifest_schemas
from runtimeV2.manifest.registry import ManifestRegistry
from runtimeV2.manifest.schema_registry import ManifestSchemaRegistry
from runtimeV2.runtime import RuntimeV2


@dataclass(frozen=True)
class ManifestStartupResult:
    """Result of manifest domain startup."""

    schema_registry: ManifestSchemaRegistry
    registry: ManifestRegistry
    capabilities: ManifestCapabilities


def startup_manifest(runtime: RuntimeV2) -> StartupResult:
    """Start the manifest domain."""

    try:
        schema_registry = ManifestSchemaRegistry()
        register_manifest_schemas(schema_registry)
        registry = ManifestRegistry()
        capabilities = register_manifest_capabilities(registry)
        runtime.register_capability("manifest_load", capabilities.load)
        runtime.register_capability("manifest_read", capabilities.read)
        runtime.register_capability("manifest_settings_read", capabilities.settings_read)
        runtime.register_capability("manifest_ui_read", capabilities.ui_read)
        runtime.register_capability("manifest_connector_read", capabilities.connector_read)
        runtime.register_capability("manifest_overlay_read", capabilities.overlay_read)
        runtime.register_domain_result("manifest", ManifestStartupResult(
            schema_registry=schema_registry,
            registry=registry,
            capabilities=capabilities,
        ))
        return startup_ok()
    except Exception as exc:
        return startup_error(f"Manifest domain startup failed: {exc}")
