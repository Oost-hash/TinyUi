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
"""Shared helpers for optional Qt-hosted features such as widgets and devtools."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, cast

from tinycore.paths import AppPaths
from tinycore.runtime.boot import HostOverlayBuild, HostStateMonitorBuild
from tinycore.runtime.core_runtime import CoreRuntime
from tinycore.runtime.plugins.participants import PluginParticipant
from tinycore.runtime.plugins.provider_activity import ProviderActivity
from tinycore.services import HostServices, RuntimeServices
from tinyqt.devtools_support import build_devtools_state_monitor_attachment
from tinywidgets.overlay import WidgetOverlay
from tinywidgets.spec import load_widgets_toml

class _StateMonitorViewModelLike(Protocol):
    REFRESH_INTERVAL_MS: int


@dataclass(frozen=True)
class DevToolsMonitorInfo:
    refresh_interval_ms: int | None


def get_devtools_monitor_info() -> DevToolsMonitorInfo:
    """Return optional devtools monitor metadata without coupling callers to the package."""
    try:
        from tinydevtools.state_monitor_viewmodel import StateMonitorViewModel
    except ImportError:
        return DevToolsMonitorInfo(refresh_interval_ms=None)
    state_monitor_cls = cast(type[_StateMonitorViewModelLike], StateMonitorViewModel)
    return DevToolsMonitorInfo(
        refresh_interval_ms=state_monitor_cls.REFRESH_INTERVAL_MS
    )


def build_widget_overlay(
    *,
    paths: AppPaths,
    host: HostServices,
    runtime: RuntimeServices,
    provider_activity: ProviderActivity,
    participants: list[PluginParticipant],
) -> HostOverlayBuild:
    """Build the shared widget overlay from registered participants."""
    overlay = WidgetOverlay(
        runtime.plugin_facts,
        provider_activity,
        paths=paths,
        widget_state_for=host.persistence.widget_state_for,
    )
    widget_sources: list[tuple[str, str, str]] = []
    for participant in participants:
        widgets_path = participant.widgets_path()
        if widgets_path is None or not widgets_path.exists():
            continue
        specs = load_widgets_toml(widgets_path)
        overlay.load(specs, plugin_name=participant.name)
        widget_sources.extend(
            (participant.name, spec.capability, spec.field)
            for spec in specs
            if spec.field
        )
    return HostOverlayBuild(overlay=overlay, widget_sources=widget_sources)


def build_devtools_runtime_attachment(
    runtime: CoreRuntime,
    overlay: object,
) -> HostStateMonitorBuild:
    """Build optional devtools runtime attachment without making callers own the package seam."""
    return build_devtools_state_monitor_attachment(runtime, cast(WidgetOverlay, overlay))
