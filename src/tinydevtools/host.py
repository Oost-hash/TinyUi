"""Optional host seam for attaching devtools to runtime and UI."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PySide6.QtQml import QQmlApplicationEngine

from tinycore.app import App
from tinycore.inspect import LogInspector, RuntimeInspector
from tinywidgets.fields import read_field
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
    core: App,
    overlay: WidgetOverlay,
    widget_sources: list[tuple[str, str, str]],
) -> DevToolsRuntimeAttachment:
    """Attach runtime diagnostics objects for the optional devtools package."""
    runtime_inspector = RuntimeInspector()
    runtime_inspector.setup(core.runtime.session, widget_sources, read_field)
    state_monitor = StateMonitorViewModel(runtime_inspector)
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
    frozen_root: str | None = None,
) -> DevToolsUiAttachment:
    """Attach devtools UI viewmodels and return the QML component path."""
    log_vm = LogViewModel(log_inspector)
    log_settings_vm = LogSettingsViewModel()
    ctx = engine.rootContext()
    ctx.setContextProperty("logViewModel", log_vm)
    ctx.setContextProperty("logSettingsViewModel", log_settings_vm)

    if frozen_root:
        qml_path = Path(frozen_root) / "tinydevtools" / "qml" / "DevToolsWindow.qml"
    else:
        qml_path = Path(__file__).resolve().parent / "qml" / "DevToolsWindow.qml"

    return DevToolsUiAttachment(
        log_view_model=log_vm,
        log_settings_view_model=log_settings_vm,
        qml_url=qml_path.resolve().as_uri(),
    )
