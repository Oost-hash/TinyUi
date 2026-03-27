"""Optional host seam for attaching devtools to runtime and UI."""

from __future__ import annotations

from dataclasses import dataclass
from PySide6.QtQml import QQmlApplicationEngine

from tinycore.logging import LogInspector
from tinycore.runtime import CoreRuntime
from tinywidgets.overlay import WidgetOverlay

from .log_settings_viewmodel import LogSettingsViewModel
from .log_viewmodel import LogViewModel
from .state_monitor_viewmodel import StateMonitorViewModel


@dataclass(frozen=True)
class DevToolsRuntimeAttachment:
    state_monitor: StateMonitorViewModel
    extra_context: dict[str, object]


@dataclass(frozen=True)
class DevToolsUiAttachment:
    log_view_model: LogViewModel
    log_settings_view_model: LogSettingsViewModel
    qml_url: str

def attach_runtime(
    core: CoreRuntime,
    overlay: WidgetOverlay,
) -> DevToolsRuntimeAttachment:
    """Attach runtime diagnostics objects for the optional devtools package."""
    if core.runtime_inspector is None:
        raise RuntimeError("CoreRuntime does not have a runtime_inspector attached")
    state_monitor = StateMonitorViewModel(core.runtime_inspector)
    for context in overlay.model.contexts:
        state_monitor.register_object(f"Widget: {context.title}", context)
    return DevToolsRuntimeAttachment(
        state_monitor=state_monitor,
        extra_context={"stateMonitorViewModel": state_monitor},
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
    ctx = engine.rootContext()
    ctx.setContextProperty("logViewModel", log_vm)
    ctx.setContextProperty("logSettingsViewModel", log_settings_vm)

    return DevToolsUiAttachment(
        log_view_model=log_vm,
        log_settings_view_model=log_settings_vm,
        qml_url=qml_path.resolve().as_uri(),
    )
