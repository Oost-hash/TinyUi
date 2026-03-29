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
"""Optional host seam for attaching devtools to runtime and UI."""

# pyright: reportCallIssue=false, reportGeneralTypeIssues=false, reportReturnType=false, reportArgumentType=false

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from PySide6.QtQml import QQmlApplicationEngine

from tinycore.logging import LogInspector
from tinycore.runtime.core_runtime import CoreRuntime
from tinyqt.registration import SingletonRegistration, register_singletons
from tinywidgets.overlay import WidgetOverlay

from .log_settings_viewmodel import LogSettingsViewModel
from .log_viewmodel import LogViewModel
from .runtime_viewmodel import RuntimeViewModel
from .state_monitor_viewmodel import StateMonitorViewModel


class _MonitorLike(Protocol):
    @property
    def refresh_interval_ms(self) -> int: ...

    def start(self) -> None: ...
    def shutdown(self) -> None: ...


@dataclass(frozen=True)
class DevToolsRuntimeAttachment:
    state_monitor: _MonitorLike
    runtime_view_model: RuntimeViewModel
    extra_context: dict[str, tuple[type, str, object]]


@dataclass(frozen=True)
class DevToolsUiAttachment:
    log_view_model: LogViewModel
    log_settings_view_model: LogSettingsViewModel
    qml_url: str


class _DevToolsMonitor(_MonitorLike):
    def __init__(
        self,
        state_monitor: StateMonitorViewModel,
        runtime_view_model: RuntimeViewModel,
    ) -> None:
        self._state_monitor = state_monitor
        self._runtime_view_model = runtime_view_model

    @property
    def refresh_interval_ms(self) -> int:
        return min(
            self._state_monitor.refresh_interval_ms,
            self._runtime_view_model.refresh_interval_ms,
        )

    def start(self) -> None:
        self._state_monitor.start()
        self._runtime_view_model.start()

    def shutdown(self) -> None:
        self._state_monitor.shutdown()
        self._runtime_view_model.shutdown()


def attach_runtime(
    core: CoreRuntime,
    overlay: WidgetOverlay,
) -> DevToolsRuntimeAttachment:
    """Attach runtime diagnostics objects for the optional devtools package."""
    if core.runtime_inspector is None:
        raise RuntimeError("CoreRuntime does not have a runtime_inspector attached")
    state_monitor = StateMonitorViewModel(core.runtime_inspector)
    runtime_view_model = RuntimeViewModel(core)
    for context in overlay.model.contexts:
        state_monitor.register_object(f"Widget: {context.title}", context)
    return DevToolsRuntimeAttachment(
        state_monitor=_DevToolsMonitor(state_monitor, runtime_view_model),
        runtime_view_model=runtime_view_model,
        extra_context={
            "StateMonitorViewModel": (
                StateMonitorViewModel,
                "TinyDevTools",
                state_monitor,
            ),
            "RuntimeViewModel": (RuntimeViewModel, "TinyDevTools", runtime_view_model),
        },
    )


def attach_ui(
    engine: QQmlApplicationEngine,
    log_inspector: LogInspector,
    *,
    qml_path,
) -> DevToolsUiAttachment:
    """Attach devtools UI viewmodels and return the QML component path."""
    log_vm = LogViewModel(log_inspector)
    log_settings_vm = LogSettingsViewModel()
    register_singletons(
        [
            SingletonRegistration(
                LogViewModel, "TinyDevTools", "LogViewModel", log_vm
            ),
            SingletonRegistration(
                LogSettingsViewModel,
                "TinyDevTools",
                "LogSettingsViewModel",
                log_settings_vm,
            ),
        ]
    )

    return DevToolsUiAttachment(
        log_view_model=log_vm,
        log_settings_view_model=log_settings_vm,
        qml_url=qml_path.resolve().as_uri(),
    )
