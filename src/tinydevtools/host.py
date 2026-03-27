"""Optional host seam for attaching devtools to runtime and UI."""

from __future__ import annotations

from dataclasses import dataclass
from PySide6.QtQml import QQmlApplicationEngine

from tinycore.app import App
from tinycore.inspect import (
    InspectionSnapshot,
    LogInspector,
    RuntimeInspector,
)
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


def _render_value(value: object) -> str:
    if isinstance(value, int | float):
        return f"{float(value):.6g}"
    return str(value)


def _provider_snapshot(provider: object) -> InspectionSnapshot:
    snapshot = getattr(provider, "inspect_snapshot", None)
    if snapshot is None:
        return [("provider.inspect", "err: provider does not implement inspect_snapshot()")]
    try:
        return snapshot()
    except Exception as exc:
        return [("provider.inspect", f"err: {exc}")]


def _field_snapshot(
    capability: str,
    provider: object,
    fields: list[str],
) -> InspectionSnapshot:
    entries: InspectionSnapshot = []
    for field in fields:
        try:
            value = read_field(capability, field, provider)
            entries.append((field, _render_value(value)))
        except Exception as exc:
            entries.append((field, f"err: {exc}"))
    return entries


def _attach_runtime_sources(
    runtime_inspector: RuntimeInspector,
    core: App,
    widget_sources: list[tuple[str, str, str]],
) -> None:
    by_consumer: dict[str, dict[str, list[str]]] = {}
    for consumer_name, capability, field in widget_sources:
        by_consumer.setdefault(consumer_name, {}).setdefault(capability, []).append(field)

    for consumer_name, fields_by_capability in by_consumer.items():
        seen_provider_names: set[str] = set()
        for capability, fields in fields_by_capability.items():
            binding = core.runtime.session.bindings_for(consumer_name).get(capability)
            if binding is None:
                continue

            if binding.provider_name not in seen_provider_names:
                handle = core.runtime.session.provider(binding.provider_name)
                if handle is not None:
                    runtime_inspector.add_snapshot_source(
                        f"provider:{binding.provider_name}:telemetry",
                        f"State: {binding.provider_name}",
                        "provider",
                        lambda provider=handle.provider: _provider_snapshot(provider),
                    )
                    seen_provider_names.add(binding.provider_name)

            runtime_inspector.add_snapshot_source(
                f"field:{consumer_name}:{capability}",
                f"Polling: {consumer_name} [{capability}]",
                "field",
                lambda capability=capability, provider=binding.provider, fields=list(fields): (
                    _field_snapshot(capability, provider, fields)
                ),
            )


def attach_runtime(
    core: App,
    overlay: WidgetOverlay,
    widget_sources: list[tuple[str, str, str]],
) -> DevToolsRuntimeAttachment:
    """Attach runtime diagnostics objects for the optional devtools package."""
    runtime_inspector = RuntimeInspector()
    _attach_runtime_sources(runtime_inspector, core, widget_sources)
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
