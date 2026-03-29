"""Host-owned helpers for wiring optional devtools surfaces into tinyqt."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, cast

from PySide6.QtQml import QQmlApplicationEngine

from tinycore.logging import LogInspector
from tinycore.runtime.core_runtime import CoreRuntime
from tinycore.runtime.boot import HostStateMonitorBuild
from tinyqt.registration import SingletonRegistration, register_singletons
from tinywidgets.overlay import WidgetOverlay
from tinyqt_devtools.log_settings_viewmodel import LogSettingsViewModel
from tinyqt_devtools.log_viewmodel import LogViewModel
from tinyqt_devtools.state_monitor_viewmodel import StateMonitorViewModel

LogViewModelClass = cast(Any, LogViewModel)
LogSettingsViewModelClass = cast(Any, LogSettingsViewModel)
StateMonitorViewModelClass = cast(Any, StateMonitorViewModel)


class _MonitorLike(Protocol):
    @property
    def refresh_interval_ms(self) -> int: ...

    def start(self) -> None: ...
    def shutdown(self) -> None: ...


@dataclass(frozen=True)
class DevToolsUiAttachment:
    log_view_model: object
    log_settings_view_model: object
    qml_url: str


class _DevToolsMonitor(_MonitorLike):
    def __init__(self, state_monitor: object) -> None:
        self._state_monitor = state_monitor

    @property
    def refresh_interval_ms(self) -> int:
        return cast(Any, self._state_monitor).refresh_interval_ms

    def start(self) -> None:
        cast(Any, self._state_monitor).start()

    def shutdown(self) -> None:
        cast(Any, self._state_monitor).shutdown()


def build_devtools_state_monitor_attachment(
    runtime: CoreRuntime,
    overlay: WidgetOverlay,
) -> HostStateMonitorBuild:
    """Build the optional devtools state-monitor seam for the shared host."""
    if runtime.runtime_inspector is None:
        raise RuntimeError("CoreRuntime does not have a runtime_inspector attached")
    state_monitor = StateMonitorViewModelClass(runtime.runtime_inspector)
    for context in overlay.model.contexts:
        cast(Any, state_monitor).register_object(f"Widget: {context.title}", context)
    return HostStateMonitorBuild(
        state_monitor=_DevToolsMonitor(state_monitor),
        extra_context={
            "StateMonitorViewModel": (
                StateMonitorViewModelClass,
                "TinyDevTools",
                state_monitor,
            ),
        },
    )


def attach_devtools_ui(
    _engine: QQmlApplicationEngine,
    log_inspector: LogInspector,
    *,
    qml_path,
) -> DevToolsUiAttachment:
    """Attach optional devtools UI viewmodels through the shared tinyqt host seam."""
    log_vm = LogViewModelClass(log_inspector)
    log_settings_vm = LogSettingsViewModelClass()
    register_singletons(
        [
            SingletonRegistration(
                LogViewModelClass, "TinyDevTools", "LogViewModel", log_vm
            ),
            SingletonRegistration(
                LogSettingsViewModelClass,
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
