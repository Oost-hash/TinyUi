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

"""Capability registration for runtime V2 plugins."""

from __future__ import annotations

from dataclasses import dataclass

from runtimeV2.plugins.capabilities.discovery import PluginDiscoveryCapability
from runtimeV2.plugins.capabilities.icon import PluginIconCapability
from runtimeV2.manifest.capabilities.manifest_read import ManifestRead
from runtimeV2.plugins.registry import PluginRegistry


@dataclass(frozen=True)
class PluginCapabilities:
    """Capabilities exposed by the plugins discovery slice."""

    discovery: PluginDiscoveryCapability
    icon: PluginIconCapability


def register_plugin_capabilities(registry: PluginRegistry, manifest_read: ManifestRead) -> PluginCapabilities:
    """Create plugin discovery/read capabilities."""

    return PluginCapabilities(
        discovery=PluginDiscoveryCapability(registry),
        icon=PluginIconCapability(registry, manifest_read),
    )
