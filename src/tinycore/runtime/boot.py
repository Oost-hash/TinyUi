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

"""Core-owned boot orchestration for the current TinyUi runtime."""

from __future__ import annotations

from time import perf_counter
from typing import Callable, Protocol, TypeVar

from tinycore.app import App, create_app
from tinycore.diagnostics.runtime_sources import build_runtime_inspector
from tinycore.logging import get_logger
from tinycore.paths import AppPaths
from tinycore.plugin.lifecycle import PluginLifecycleManager
from tinycore.plugin.manifest import PluginManifest, scan_plugins
from tinycore.plugin.subprocess_host import SubprocessPlugin
from tinyui.plugin import TinyUIPlugin
from tinywidgets.overlay import WidgetOverlay
from tinywidgets.spec import load_widgets_toml

from .core_runtime import CoreRuntime, build_runtime_registry
from .host_workers import HostWorkerSupervisor
from .models import RuntimeState, RuntimeUnitSpec
from .process_supervisor import ProcessSupervisor
from .scheduler import RuntimeScheduler
from .unit_ids import boot_phase_unit_id

_log = get_logger(__name__)
_T = TypeVar("_T")
_BOOT_PHASE_ORDER = (
    "register_consumers",
    "register_host",
    "activate_plugins",
    "register_providers",
    "bind_consumers",
    "build_overlay",
    "build_state_monitor",
)


class _StateMonitorLike(Protocol):
    @property
    def refresh_interval_ms(self) -> int: ...

    def start(self) -> None: ...
    def shutdown(self) -> None: ...


def _ms(start: float) -> float:
    return round((perf_counter() - start) * 1000, 1)


def _log_startup_phase(phase: str, start: float) -> None:
    _log.startup_phase(phase, _ms(start))


def _record_boot_phase(boot_phase_states: dict[str, RuntimeState], phase_name: str, state: RuntimeState) -> None:
    boot_phase_states[boot_phase_unit_id(phase_name)] = state


def _mark_remaining_boot_phases_incomplete(
    boot_phase_states: dict[str, RuntimeState],
    current_phase: str,
) -> None:
    try:
        index = _BOOT_PHASE_ORDER.index(current_phase)
    except ValueError:
        return

    for phase_name in _BOOT_PHASE_ORDER[index + 1 :]:
        phase_id = boot_phase_unit_id(phase_name)
        if boot_phase_states.get(phase_id) in {"completed", "failed", "incomplete"}:
            continue
        boot_phase_states[phase_id] = "incomplete"


def _run_pre_registry_phase(
    boot_phase_states: dict[str, RuntimeState],
    phase_name: str,
    action: Callable[[], _T],
) -> _T:
    try:
        result = action()
    except Exception:
        _record_boot_phase(boot_phase_states, phase_name, "failed")
        _mark_remaining_boot_phases_incomplete(boot_phase_states, phase_name)
        raise
    _record_boot_phase(boot_phase_states, phase_name, "completed")
    return result


def _run_registry_phase(
    runtime: CoreRuntime,
    boot_phase_states: dict[str, RuntimeState],
    phase_name: str,
    action: Callable[[], _T],
) -> _T:
    phase_id = boot_phase_unit_id(phase_name)
    runtime.units.set_state(phase_id, "running")
    boot_phase_states[phase_id] = "running"
    try:
        result = action()
    except Exception:
        runtime.units.set_state(phase_id, "failed")
        boot_phase_states[phase_id] = "failed"
        _mark_remaining_boot_phases_incomplete(boot_phase_states, phase_name)
        for remaining_phase in _BOOT_PHASE_ORDER[_BOOT_PHASE_ORDER.index(phase_name) + 1 :]:
            remaining_phase_id = boot_phase_unit_id(remaining_phase)
            if runtime.units.get(remaining_phase_id) is not None:
                runtime.units.set_state(remaining_phase_id, "incomplete")
        raise
    runtime.units.set_state(phase_id, "completed")
    boot_phase_states[phase_id] = "completed"
    return result


def discover_manifests(plugins_dir) -> list[PluginManifest]:
    """Scan the plugin directory and return runtime manifests."""
    return scan_plugins(plugins_dir)


def boot_runtime(paths: AppPaths, manifests: list[PluginManifest]) -> CoreRuntime:
    """Build and wire the runtime before the Qt event loop starts."""
    total_start = perf_counter()
    boot_phase_states: dict[str, RuntimeState] = {}
    consumer_manifests = [m for m in manifests if m.is_consumer]
    provider_manifests = [m for m in manifests if m.is_provider]
    process_supervisor = ProcessSupervisor()
    scheduler = RuntimeScheduler()

    phase_start = perf_counter()
    app = create_app(
        paths,
        *[
            (
                SubprocessPlugin(
                    m.consumer_runtime_spec(),
                    process_supervisor=process_supervisor,
                ),
                m.requires,
            )
            for m in consumer_manifests
        ],
        register_plugins=False,
    )
    _log_startup_phase("create_app", phase_start)

    phase_start = perf_counter()
    _run_pre_registry_phase(boot_phase_states, "register_consumers", lambda: _register_consumers(app))
    _log_startup_phase("register_consumers", phase_start)

    phase_start = perf_counter()
    _run_pre_registry_phase(boot_phase_states, "register_host", lambda: _register_host_and_start(app))
    _log_startup_phase("register_host", phase_start)

    phase_start = perf_counter()
    lifecycle = _run_pre_registry_phase(
        boot_phase_states,
        "activate_plugins",
        lambda: _activate_plugins(app, scheduler),
    )
    _log_startup_phase("activate_plugins", phase_start)

    phase_start = perf_counter()
    _run_pre_registry_phase(boot_phase_states, "register_providers", lambda: _register_providers(app, provider_manifests))
    _log_startup_phase("register_providers", phase_start)

    phase_start = perf_counter()
    _run_pre_registry_phase(boot_phase_states, "bind_consumers", lambda: _bind_consumers(app, consumer_manifests))
    _log_startup_phase("bind_consumers", phase_start)

    phase_start = perf_counter()
    overlay, widget_sources = _run_pre_registry_phase(
        boot_phase_states,
        "build_overlay",
        lambda: _build_overlay(app, consumer_manifests),
    )
    _log_startup_phase("build_overlay", phase_start)

    extra_context = {
        "widgetModel": overlay.model,
        "widgetOverlayState": overlay.state,
    }
    host_workers = HostWorkerSupervisor()

    registry = build_runtime_registry(
        app,
        lifecycle,
        process_supervisor,
        overlay,
        None,
        boot_phase_states=boot_phase_states,
    )
    process_supervisor.attach_registry(registry)
    lifecycle.attach_runtime_registry(registry)
    app.runtime.session.attach_runtime_registry(registry)
    host_workers.attach_registry(registry)

    def _start_overlay() -> None:
        overlay.start()
        if registry.get("ui.widgets.poll") is not None:
            registry.set_state("ui.widgets.poll", "running")

    def _stop_overlay() -> None:
        if registry.get("ui.widgets.poll") is not None:
            registry.set_state("ui.widgets.poll", "stopping")
        overlay.stop()
        if registry.get("ui.widgets.poll") is not None:
            registry.set_state("ui.widgets.poll", "stopped")

    host_workers.register(
        "ui.widgets.overlay",
        start=_start_overlay,
        stop=_stop_overlay,
    )
    host_workers.register(
        "plugins.lifecycle",
        stop=lifecycle.shutdown,
    )

    runtime = CoreRuntime(
        app=app,
        lifecycle=lifecycle,
        process_supervisor=process_supervisor,
        scheduler=scheduler,
        host_workers=host_workers,
        runtime_inspector=None,
        overlay=overlay,
        state_monitor=None,
        extra_context=extra_context,
        units=registry,
    )
    phase_start = perf_counter()
    state_monitor, devtools_context = _run_registry_phase(
        runtime,
        boot_phase_states,
        "build_state_monitor",
        lambda: _build_state_monitor(runtime, overlay, widget_sources),
    )
    _log_startup_phase("build_state_monitor", phase_start)
    _log.startup_phase("bootstrap_runtime_total", _ms(total_start))

    runtime.extra_context.update(devtools_context)
    if state_monitor is not None:
        host_unit = runtime.units.get("host.main")
        host_pid = host_unit.pid if host_unit is not None else None
        runtime.state_monitor = state_monitor
        runtime.units.declare(
            RuntimeUnitSpec(
                id="devtools.monitor",
                kind="timer",
                role="devtools.monitor",
                owner="tinydevtools",
                transport="qt_timer",
                parent_id="host.main",
                execution_policy="host",
                pid=host_pid,
                activation_policy="on_demand",
                start_order=220,
                stop_order=780,
                depends_on=("ui.widgets.overlay",),
                schedule_kind="interval",
                schedule_clock="qt",
                interval_ms=state_monitor.refresh_interval_ms,
            ),
            state="idle",
        )
        runtime.host_workers.register(
            "devtools.monitor",
            start=state_monitor.start,
            stop=state_monitor.shutdown,
        )

    runtime.runtime_inspector = build_runtime_inspector(runtime, widget_sources)
    return runtime


def _load_host_state(app: App) -> None:
    app.host.persistence.load_all()


def _register_host_and_start(app: App) -> None:
    _register_host(app)
    _load_host_state(app)
    app.start(plugins=False)


def _register_consumers(app: App) -> None:
    """Run the consumer registration phase explicitly from the runtime boot path."""
    app.register_plugins()


def _register_host(app: App) -> None:
    """Run host-side registration outside the plugin registry."""
    TinyUIPlugin().register(app)


def _activate_plugins(app: App, scheduler: RuntimeScheduler) -> PluginLifecycleManager:
    lifecycle = PluginLifecycleManager(
        app.runtime.plugins,
        scheduler=scheduler,
        grace_seconds=30.0,
    )
    lifecycle.attach_session(app.runtime.session)
    plugin_names = [p.name for p in app.runtime.plugins.plugins]
    if plugin_names:
        lifecycle.activate(plugin_names[0])
    return lifecycle


def _register_providers(app: App, manifests: list[PluginManifest]) -> None:
    for manifest in manifests:
        if manifest.provider is None:
            continue
        provider = manifest.provider.create()
        provider.open()
        app.runtime.session.register_provider(manifest.name, provider, manifest.exports)
        _log.info(
            "provider registered  plugin=%s  type=%s  exports=%s",
            manifest.name,
            type(provider).__name__,
            ", ".join(manifest.exports) if manifest.exports else "-",
        )


def _bind_consumers(app: App, manifests: list[PluginManifest]) -> None:
    for manifest in manifests:
        bindings = app.runtime.session.bind_consumer(
            manifest.name,
            manifest.requires,
            manifest.provider_requests,
        )
        if bindings.missing:
            _log.warning(
                "consumer requires missing  plugin=%s  missing=%s",
                manifest.name,
                ", ".join(bindings.missing),
            )
            continue
        if bindings.resolved:
            _log.info(
                "consumer bound  plugin=%s  requires=%s",
                manifest.name,
                ", ".join(
                    f"{capability}->{binding.provider_name}"
                    for capability, binding in bindings.resolved.items()
                ),
            )


def _build_overlay(
    app: App,
    manifests: list[PluginManifest],
) -> tuple[WidgetOverlay, list[tuple[str, str, str]]]:
    overlay = WidgetOverlay(
        app.runtime.session,
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
        widget_sources.extend((manifest.name, spec.capability, spec.field) for spec in specs if spec.field)
    return overlay, widget_sources


def _build_state_monitor(
    runtime: CoreRuntime,
    overlay: WidgetOverlay,
    widget_sources: list[tuple[str, str, str]],
) -> tuple[_StateMonitorLike | None, dict[str, object]]:
    try:
        from tinydevtools.host import attach_runtime
    except ImportError:
        _log.info("devtools runtime attachment unavailable")
        return None, {}

    attachment = attach_runtime(runtime, overlay)
    return attachment.state_monitor, attachment.extra_context
