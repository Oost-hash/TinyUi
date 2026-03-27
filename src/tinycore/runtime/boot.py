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

from dataclasses import dataclass
from time import perf_counter
from typing import Callable, Protocol, TypeVar, cast

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
from .host_workers import HostWorkerHandle, HostWorkerSupervisor
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


@dataclass(frozen=True)
class _OverlayBuild:
    overlay: WidgetOverlay
    widget_sources: list[tuple[str, str, str]]


@dataclass(frozen=True)
class _StateMonitorBuild:
    state_monitor: _StateMonitorLike | None
    extra_context: dict[str, object]


@dataclass(frozen=True)
class _HostWorkerBuild:
    workers: tuple[HostWorkerHandle, ...]


@dataclass(frozen=True)
class _PreRegistryPhaseSpec:
    name: str
    action: Callable[[], object]
    assign: Callable[[object], None] | None = None


@dataclass(frozen=True)
class _RegistryPhaseSpec:
    name: str
    action: Callable[[], object]


@dataclass
class _BootAssembly:
    paths: AppPaths
    manifests: list[PluginManifest]
    consumer_manifests: list[PluginManifest]
    provider_manifests: list[PluginManifest]
    boot_phase_states: dict[str, RuntimeState]
    process_supervisor: ProcessSupervisor
    scheduler: RuntimeScheduler
    app: App
    devtools_monitor_interval_ms: int | None
    lifecycle: PluginLifecycleManager | None = None
    overlay_build: _OverlayBuild | None = None
    host_worker_build: _HostWorkerBuild | None = None


class _StateMonitorLike(Protocol):
    @property
    def refresh_interval_ms(self) -> int: ...

    def start(self) -> None: ...
    def shutdown(self) -> None: ...


def _ms(start: float) -> float:
    return round((perf_counter() - start) * 1000, 1)


def _log_startup_phase(phase: str, start: float) -> None:
    _log.startup_phase(phase, _ms(start))


def _record_boot_phase(
    boot_phase_states: dict[str, RuntimeState], phase_name: str, state: RuntimeState
) -> None:
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
        for remaining_phase in _BOOT_PHASE_ORDER[
            _BOOT_PHASE_ORDER.index(phase_name) + 1 :
        ]:
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
    assembly = _create_boot_assembly(paths, manifests)
    _run_pre_registry_phases(assembly, _pre_registry_phases(assembly))
    lifecycle = assembly.lifecycle
    overlay_build = assembly.overlay_build
    if lifecycle is None or overlay_build is None:
        raise RuntimeError("boot assembly is incomplete after required runtime phases")

    extra_context = {
        "widgetModel": overlay_build.overlay.model,
        "widgetOverlayState": overlay_build.overlay.state,
    }
    host_workers = HostWorkerSupervisor()

    registry = build_runtime_registry(
        assembly.app,
        lifecycle,
        assembly.process_supervisor,
        overlay_build.overlay,
        None,
        devtools_monitor_interval_ms=assembly.devtools_monitor_interval_ms,
        boot_phase_states=assembly.boot_phase_states,
    )
    assembly.process_supervisor.attach_registry(registry)
    lifecycle.attach_runtime_registry(registry)
    assembly.app.runtime.session.attach_runtime_registry(registry)
    host_workers.attach_registry(registry)

    def _start_overlay() -> None:
        overlay_build.overlay.start()
        if registry.get("ui.widgets.poll") is not None:
            registry.set_state("ui.widgets.poll", "running")

    def _stop_overlay() -> None:
        if registry.get("ui.widgets.poll") is not None:
            registry.set_state("ui.widgets.poll", "stopping")
        overlay_build.overlay.stop()
        if registry.get("ui.widgets.poll") is not None:
            registry.set_state("ui.widgets.poll", "stopped")

    assembly.host_worker_build = _build_host_workers(
        lifecycle,
        state_monitor=None,
        start_overlay=_start_overlay,
        stop_overlay=_stop_overlay,
    )
    _register_host_workers(host_workers, assembly.host_worker_build)

    runtime = CoreRuntime(
        app=assembly.app,
        lifecycle=lifecycle,
        process_supervisor=assembly.process_supervisor,
        scheduler=assembly.scheduler,
        host_workers=host_workers,
        runtime_inspector=None,
        overlay=overlay_build.overlay,
        state_monitor=None,
        extra_context=extra_context,
        units=registry,
    )
    state_monitor_build = cast(
        _StateMonitorBuild,
        _run_registry_phases(
        runtime,
        assembly.boot_phase_states,
        (
            _RegistryPhaseSpec(
                name="build_state_monitor",
                action=lambda: _build_state_monitor(
                    runtime,
                    overlay_build.overlay,
                    overlay_build.widget_sources,
                ),
            ),
        ),
        )[0],
    )
    _log.startup_phase("bootstrap_runtime_total", _ms(total_start))

    runtime.extra_context.update(state_monitor_build.extra_context)
    if state_monitor_build.state_monitor is not None:
        runtime.state_monitor = state_monitor_build.state_monitor
        assembly.host_worker_build = _build_host_workers(
            lifecycle,
            state_monitor=state_monitor_build.state_monitor,
            start_overlay=_start_overlay,
            stop_overlay=_stop_overlay,
        )
        _register_host_workers(runtime.host_workers, assembly.host_worker_build)

    runtime.runtime_inspector = build_runtime_inspector(
        runtime, overlay_build.widget_sources
    )
    return runtime


def _create_boot_assembly(
    paths: AppPaths, manifests: list[PluginManifest]
) -> _BootAssembly:
    """Build the early boot assembly inputs before phase orchestration begins."""
    boot_phase_states: dict[str, RuntimeState] = {}
    consumer_manifests = [m for m in manifests if m.is_consumer]
    provider_manifests = [m for m in manifests if m.is_provider]
    process_supervisor = ProcessSupervisor()
    scheduler = RuntimeScheduler()
    devtools_monitor_interval_ms = _devtools_monitor_interval_ms()

    phase_start = perf_counter()
    app = create_app(
        paths,
        *[
            (
                SubprocessPlugin(
                    manifest.consumer_runtime_spec(),
                    process_supervisor=process_supervisor,
                ),
                manifest.requires,
            )
            for manifest in consumer_manifests
        ],
        register_plugins=False,
    )
    _log_startup_phase("create_app", phase_start)

    return _BootAssembly(
        paths=paths,
        manifests=manifests,
        consumer_manifests=consumer_manifests,
        provider_manifests=provider_manifests,
        boot_phase_states=boot_phase_states,
        process_supervisor=process_supervisor,
        scheduler=scheduler,
        app=app,
        devtools_monitor_interval_ms=devtools_monitor_interval_ms,
    )


def _pre_registry_phases(assembly: _BootAssembly) -> tuple[_PreRegistryPhaseSpec, ...]:
    """Describe pre-registry boot phases as assembly data."""
    return (
        _PreRegistryPhaseSpec(
            name="register_consumers",
            action=lambda: _register_consumers(assembly.app),
        ),
        _PreRegistryPhaseSpec(
            name="register_host",
            action=lambda: _register_host_and_start(assembly.app),
        ),
        _PreRegistryPhaseSpec(
            name="activate_plugins",
            action=lambda: _activate_plugins(assembly.app, assembly.scheduler),
            assign=lambda result: setattr(assembly, "lifecycle", result),
        ),
        _PreRegistryPhaseSpec(
            name="register_providers",
            action=lambda: _register_providers(assembly.app, assembly.provider_manifests),
        ),
        _PreRegistryPhaseSpec(
            name="bind_consumers",
            action=lambda: _bind_consumers(assembly.app, assembly.consumer_manifests),
        ),
        _PreRegistryPhaseSpec(
            name="build_overlay",
            action=lambda: _build_overlay(assembly.app, assembly.consumer_manifests),
            assign=lambda result: setattr(assembly, "overlay_build", result),
        ),
    )


def _run_pre_registry_phases(
    assembly: _BootAssembly,
    phases: tuple[_PreRegistryPhaseSpec, ...],
) -> None:
    """Run the pre-registry phase list with shared timing and failure handling."""
    for phase in phases:
        phase_start = perf_counter()
        result = _run_pre_registry_phase(
            assembly.boot_phase_states,
            phase.name,
            phase.action,
        )
        if phase.assign is not None:
            phase.assign(result)
        _log_startup_phase(phase.name, phase_start)


def _run_registry_phases(
    runtime: CoreRuntime,
    boot_phase_states: dict[str, RuntimeState],
    phases: tuple[_RegistryPhaseSpec, ...],
) -> tuple[object, ...]:
    """Run runtime-aware phase specs with shared timing and phase state updates."""
    results: list[object] = []
    for phase in phases:
        phase_start = perf_counter()
        results.append(
            _run_registry_phase(
                runtime,
                boot_phase_states,
                phase.name,
                phase.action,
            )
        )
        _log_startup_phase(phase.name, phase_start)
    return tuple(results)


def _devtools_monitor_interval_ms() -> int | None:
    """Return the optional devtools monitor refresh interval for boot assembly."""
    try:
        from tinydevtools.state_monitor_viewmodel import StateMonitorViewModel
    except ImportError:
        return None
    return StateMonitorViewModel.REFRESH_INTERVAL_MS


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
) -> _OverlayBuild:
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
        widget_sources.extend(
            (manifest.name, spec.capability, spec.field) for spec in specs if spec.field
        )
    return _OverlayBuild(overlay=overlay, widget_sources=widget_sources)


def _build_state_monitor(
    runtime: CoreRuntime,
    overlay: WidgetOverlay,
    widget_sources: list[tuple[str, str, str]],
) -> _StateMonitorBuild:
    try:
        from tinydevtools.host import attach_runtime
    except ImportError:
        _log.info("devtools runtime attachment unavailable")
        return _StateMonitorBuild(state_monitor=None, extra_context={})

    attachment = attach_runtime(runtime, overlay)
    return _StateMonitorBuild(
        state_monitor=attachment.state_monitor,
        extra_context=attachment.extra_context,
    )


def _build_host_workers(
    lifecycle: PluginLifecycleManager,
    *,
    state_monitor: _StateMonitorLike | None,
    start_overlay: Callable[[], None],
    stop_overlay: Callable[[], None],
) -> _HostWorkerBuild:
    """Describe host worker registration as boot assembly data."""
    workers = [
        HostWorkerHandle(
            unit_id="ui.widgets.overlay",
            start=start_overlay,
            stop=stop_overlay,
        ),
        HostWorkerHandle(
            unit_id="plugins.lifecycle",
            stop=lifecycle.shutdown,
        ),
    ]
    if state_monitor is not None:
        workers.append(
            HostWorkerHandle(
                unit_id="devtools.monitor",
                start=state_monitor.start,
                stop=state_monitor.shutdown,
            )
        )
    return _HostWorkerBuild(workers=tuple(workers))


def _register_host_workers(
    supervisor: HostWorkerSupervisor, build: _HostWorkerBuild
) -> None:
    """Attach the described host worker surfaces to the supervisor."""
    for worker in build.workers:
        supervisor.register(worker.unit_id, start=worker.start, stop=worker.stop)
