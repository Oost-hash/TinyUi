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
"""TinyUI-owned host assembly for the core runtime boot seam."""

# pyright: reportAttributeAccessIssue=false

from __future__ import annotations

from dataclasses import dataclass

from tinycore.logging import get_logger
from tinycore.paths import AppPaths
from tinycore.runtime.boot import HostAssembly, HostOverlayBuild, HostStateMonitorBuild
from tinycore.runtime.core_runtime import CoreRuntime
from tinycore.runtime.plugins.participants import PluginParticipant
from tinycore.runtime.plugins.provider_activity import ProviderActivity
from tinycore.services import HostServices, RuntimeServices
from tinyqt.attachments import (
    build_devtools_runtime_attachment,
    build_widget_overlay,
    get_devtools_monitor_info,
)

from .plugin import TinyUIPlugin

_log = get_logger(__name__)


@dataclass(frozen=True)
class TinyUiHostAssembly(HostAssembly):
    """Host-owned assembly for TinyUI surfaces that sit on top of the runtime."""

    @property
    def devtools_monitor_interval_ms(self) -> int | None:
        return get_devtools_monitor_info().refresh_interval_ms

    def register_host(self, host: HostServices) -> None:
        TinyUIPlugin().register(host)

    def startup_participant(self, host: HostServices) -> str | None:
        return host.persistence.get_setting("TinyUI", "startup_plugin") or None

    def build_overlay(
        self,
        paths: AppPaths,
        host: HostServices,
        runtime: RuntimeServices,
        provider_activity: ProviderActivity,
        participants: list[PluginParticipant],
    ) -> HostOverlayBuild:
        return build_widget_overlay(
            paths=paths,
            host=host,
            runtime=runtime,
            provider_activity=provider_activity,
            participants=participants,
        )

    def build_state_monitor(
        self,
        runtime: CoreRuntime,
        overlay: object,
        widget_sources: list[tuple[str, str, str]],
    ) -> HostStateMonitorBuild:
        return build_devtools_runtime_attachment(runtime, overlay)


TINYUI_HOST_ASSEMBLY = TinyUiHostAssembly()
