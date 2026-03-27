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

"""Core composition root for explicit host/runtime service assembly."""

from __future__ import annotations

from dataclasses import dataclass

from .paths import AppPaths
from .runtime.plugins.consumer import PluginParticipant
from .services import HostServices, RuntimeServices, build_host_services, build_runtime_services


@dataclass(frozen=True)
class RuntimeComposition:
    """Explicit composition data for a booted runtime host."""

    paths: AppPaths
    host: HostServices
    runtime: RuntimeServices

    def start(self, *, plugins: bool = True) -> None:
        """Start the composition, optionally starting all plugins."""
        if plugins:
            self.runtime.plugin_runtime.start_all()

    def stop(self) -> None:
        """Stop the composition and all registered plugins."""
        self.runtime.plugin_runtime.stop_all()

    def register_plugins(self) -> None:
        """Run plugin register phase with scoped plugin contexts."""
        self.runtime.plugin_runtime.register_all(self.host, self.runtime)

def create_runtime_composition(
    paths: AppPaths,
    *plugins: PluginParticipant,
    register_plugins: bool = True,
) -> RuntimeComposition:
    """Factory: create explicit host/runtime service composition data."""
    composition = RuntimeComposition(
        paths=paths,
        host=build_host_services(paths),
        runtime=build_runtime_services(),
    )
    for plugin in plugins:
        composition.runtime.plugin_runtime.add(plugin)
    if register_plugins:
        composition.register_plugins()
    return composition
