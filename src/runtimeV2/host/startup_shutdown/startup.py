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

"""Startup for the runtime V2 host domain."""

from __future__ import annotations

from dataclasses import dataclass

from runtimeV2.schemas.startup import StartupResult, startup_error, startup_ok
from runtimeV2.host.contracts import HostShell
from runtimeV2.host.policy import build_host_shell
from runtimeV2.host.startup_shutdown.register_capabilities import HostCapabilities, register_host_capabilities
from runtimeV2.manifest.capabilities.manifest_read import ManifestRead
from runtimeV2.runtime import RuntimeV2


@dataclass(frozen=True)
class HostStartupResult:
    """Result of host domain startup."""

    host_shell: HostShell
    capabilities: HostCapabilities


def startup_host(runtime: RuntimeV2) -> StartupResult:
    """Start the host domain from plugin read models."""

    try:
        manifest_read = runtime.capability("manifest_read", ManifestRead)
        host_shell = build_host_shell(manifest_read.all_manifests())
        capabilities = register_host_capabilities(host_shell)
        runtime.register_capability("app_identity_read", capabilities.app_identity_read)
        runtime.register_capability("host_shell_read", capabilities.host_shell_read)
        runtime.register_capability("main_window_read", capabilities.main_window_read)
        runtime.register_domain_result("host", HostStartupResult(
            host_shell=host_shell,
            capabilities=capabilities,
        ))
        return startup_ok()
    except Exception as exc:
        return startup_error(f"Host domain startup failed: {exc}")

