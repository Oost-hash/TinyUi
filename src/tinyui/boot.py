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

#  TinyUI
"""TinyUI-owned host assembly for the core runtime boot seam."""

from __future__ import annotations

from dataclasses import dataclass
from typing import cast

from tinycore.app import App
from tinycore.logging import get_logger
from tinycore.plugin.manifest import PluginManifest
from tinycore.runtime.boot import HostAssembly, HostOverlayBuild, HostStateMonitorBuild
from tinycore.runtime.core_runtime import CoreRuntime
from tinycore.runtime.provider_activity import ProviderActivity
from tinywidgets.overlay import WidgetOverlay
from tinywidgets.spec import load_widgets_toml

from .plugin import TinyUIPlugin

_log = get_logger(__name__)


@dataclass(frozen=True)
class TinyUiHostAssembly(HostAssembly):
    """Host-owned assembly for TinyUI surfaces that sit on top of the runtime."""

    @property
    def devtools_monitor_interval_ms(self) -> int | None:
        try:
            from tinydevtools.state_monitor_viewmodel import StateMonitorViewModel
        except ImportError:
            return None
        return StateMonitorViewModel.REFRESH_INTERVAL_MS

    def register_host(self, app: App) -> None:
        TinyUIPlugin().register(app)

    def build_overlay(
        self,
        app: App,
        provider_activity: ProviderActivity,
        manifests: list[PluginManifest],
    ) -> HostOverlayBuild:
        overlay = WidgetOverlay(
            app.runtime.session,
            provider_activity,
            paths=app.paths,
            widget_state_for=app.host.persistence.widget_state_for,
        )
        widget_sources: list[tuple[str, str, str]] = []
        for manifest in manifests:
            widgets_path = manifest.widgets_path()
            if widgets_path is None or not widgets_path.exists():
                continue
            specs = load_widgets_toml(widgets_path)
            overlay.load(specs, plugin_name=manifest.name)
            widget_sources.extend(
                (manifest.name, spec.capability, spec.field)
                for spec in specs
                if spec.field
            )
        return HostOverlayBuild(overlay=overlay, widget_sources=widget_sources)

    def build_state_monitor(
        self,
        runtime: CoreRuntime,
        overlay: object,
        widget_sources: list[tuple[str, str, str]],
    ) -> HostStateMonitorBuild:
        try:
            from tinydevtools.host import attach_runtime
        except ImportError:
            _log.info("devtools runtime attachment unavailable")
            return HostStateMonitorBuild(state_monitor=None, extra_context={})

        attachment = attach_runtime(runtime, cast(WidgetOverlay, overlay))
        return HostStateMonitorBuild(
            state_monitor=attachment.state_monitor,
            extra_context=attachment.extra_context,
        )


TINYUI_HOST_ASSEMBLY = TinyUiHostAssembly()
