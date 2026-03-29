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
"""WidgetOverlay — manages widget contexts and native tinyqt widget surfaces."""

# pyright: reportCallIssue=false, reportGeneralTypeIssues=false, reportReturnType=false

from __future__ import annotations

from typing import Callable, cast

from tinyruntime_schema import get_logger
from tinycore.paths import AppPaths
from tinycore.persistence.widget_state import WidgetStateStore
from tinyruntime.plugins.facts import PluginParticipationFacts
from tinyruntime.plugins.provider_activity import ProviderActivity
from tinyruntime.plugins.provider_refresh import ProviderRefreshParticipant
from tinyruntime.update_loop import RuntimeUpdateLoop
from tinyqt.widget_host import WidgetSurfaceHost, WidgetSurfacePaths
from tinyqt.registration import RegistrationMap
from .context import WidgetContext, WidgetModel, WidgetOverlayState
from .spec import WidgetSpec
from .state_participant import WidgetStateParticipant

_log = get_logger(__name__)


class WidgetOverlay:
    """Creates and manages all widget windows.

    Usage (from composition root):
        overlay = WidgetOverlay(session, paths=core.paths)
        overlay.load(specs, plugin_name="demo")
        exit_code = tinyqt_main.launch(core, lifecycle, pre_run=overlay.start,
                                  extra_context=overlay.extra_context)
    """

    def __init__(self, participation: PluginParticipationFacts,
                 provider_activity: ProviderActivity,
                 paths: AppPaths | None = None,
                 widget_state_for: Callable[[str], WidgetStateStore | None] | None = None) -> None:
        self._participation = participation
        self._provider_activity = provider_activity
        self._paths = paths
        self._widget_state_for = widget_state_for
        self._update_loop = RuntimeUpdateLoop(interval_ms=100)
        self._model = WidgetModel()
        self._state = WidgetOverlayState()
        self._surface_host: WidgetSurfaceHost | None = None

        self._update_loop.register_refresh_participant(
            ProviderRefreshParticipant(provider_activity),
            label="provider.refresh",
        )

    @property
    def model(self) -> WidgetModel:
        """The widget model — can be registered in any QML engine."""
        return self._model

    @property
    def state(self) -> WidgetOverlayState:
        """Shared overlay state used by both the main UI and widget engine."""
        return self._state

    @property
    def extra_context(self) -> RegistrationMap:
        """Singleton registrations for the main QML engine."""
        return {
            "WidgetModel": (WidgetModel, "TinyWidgets", self._model),
            "WidgetOverlayState": (WidgetOverlayState, "TinyWidgets", self._state),
        }

    @property
    def update_interval_ms(self) -> int:
        """Return the interval of the runtime-owned widget update loop."""
        return self._update_loop.interval_ms

    def update_participants(self) -> tuple[tuple[str, str], ...]:
        """Expose update participants as (stage, label) pairs for diagnostics."""
        return tuple(
            (info.stage, info.label)
            for info in self._update_loop.participant_infos()
        )

    def load(self, specs: list[WidgetSpec], plugin_name: str) -> None:
        """Create a state participant + context for every enabled widget spec."""
        store = self._widget_state_for(plugin_name) if self._widget_state_for is not None else None

        for spec in specs:
            if not spec.capability or not spec.field:
                continue

            # Override spec defaults with persisted user config
            if store:
                saved = store.get(spec.id)
                if saved:
                    spec.enable      = saved.get("enable", spec.enable)
                    spec.x           = saved.get("x", spec.x)
                    spec.y           = saved.get("y", spec.y)
                    spec.label       = saved.get("label", spec.label)
                    if "thresholds" in saved:
                        from .threshold import ThresholdEntry
                        spec.thresholds = [
                            ThresholdEntry(
                                t["value"],
                                t["color"],
                                t.get("flash",                        False),
                                t.get("flashSpeed",  t.get("flash_speed",  5)),
                                t.get("flashTarget", t.get("flash_target", "value")),
                            )
                            for t in saved["thresholds"]
                        ]

            ctx = WidgetContext(spec, self._participation.controls, plugin_name)
            participant = WidgetStateParticipant(
                spec,
                self._participation,
                plugin_name,
                ctx.update,
            )

            if store:
                def _save(cx: WidgetContext = ctx, s: WidgetStateStore = store) -> None:
                    s.save(
                        cx._spec.id,
                        cx._spec.enable,
                        cx._spec.x,
                        cx._spec.y,
                        cx._spec.label,
                        cast(list[dict[str, object]], cx.thresholds),
                    )

                ctx.positionChanged.connect(_save)
                ctx.configChanged.connect(_save)

            self._model.add(ctx)
            self._update_loop.register_derived_participant(
                participant,
                label=f"widget.state:{spec.id}",
            )
            _log.overlay(
                "loaded widget",
                id=spec.id,
                capability=spec.capability,
                field=spec.field,
            )

    def start(self) -> None:
        """Create widget windows and start runtime-driven updates.

        Must be called after QApplication exists (i.e. inside pre_run).
        """
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        if app is not None:
            app.aboutToQuit.connect(self.stop)

        self._start_surface_host()
        _log.overlay("widget surface host active", widgets=self._model.rowCount())
        self._update_loop.start()

    def stop(self) -> None:
        if self._surface_host is not None:
            self._surface_host.stop()
            self._surface_host = None
        self._update_loop.stop()
        _log.overlay("stopping")

    def _start_surface_host(self) -> None:
        if self._paths is None:
            raise RuntimeError("WidgetOverlay requires AppPaths for tinyqt surface hosting")
        surface_paths = WidgetSurfacePaths.from_app_paths(self._paths)
        host = WidgetSurfaceHost(
            paths=surface_paths,
            model=self._model,
            overlay_state=self._state,
        )
        host.start()
        self._surface_host = host
