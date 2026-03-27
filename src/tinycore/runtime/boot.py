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

from tinycore.composition import create_runtime_composition
from tinycore.diagnostics.runtime_sources import build_runtime_inspector
from tinycore.logging import get_logger
from tinycore.paths import AppPaths
from tinycore.plugin.lifecycle import PluginLifecycleManager
from tinycore.plugin.manifest import PluginManifest, scan_plugins
from tinycore.plugin.subprocess_host import SubprocessPlugin
from tinycore.services import HostServices, RuntimeServices

from .core_runtime import CoreRuntime, build_runtime_registry
from .host_workers import HostWorkerHandle, HostWorkerSupervisor
from .models import RuntimeState
from .process_supervisor import ProcessSupervisor
from .provider_activity import ProviderActivity
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
class HostOverlayBuild:
    overlay: _OverlayLike
    widget_sources: list[tuple[str, str, str]]


@dataclass(frozen=True)
class HostStateMonitorBuild:
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
    host: HostServices
    runtime: RuntimeServices
    start_runtime: Callable[[], None]
    stop_runtime: Callable[[], None]
    host_assembly: HostAssembly
    provider_activity: ProviderActivity | None = None
    lifecycle: PluginLifecycleManager | None = None
    overlay_build: HostOverlayBuild | None = None
    host_worker_build: _HostWorkerBuild | None = None


class _OverlayLike(Protocol):
    @property
    def model(self) -> object: ...

    @property
    def state(self) -> object: ...

    @property
    def poll_interval_ms(self) -> int: ...

    def start(self) -> None: ...
    def stop(self) -> None: ...


class _StateMonitorLike(Protocol):
    @property
    def refresh_interval_ms(self) -> int: ...

    def start(self) -> None: ...
    def shutdown(self) -> None: ...


class HostAssembly(Protocol):
    @property
    def devtools_monitor_interval_ms(self) -> int | None: ...

    def register_host(self, host: HostServices) -> None: ...

    def build_overlay(
        self,
        paths: AppPaths,
        host: HostServices,
        runtime: RuntimeServices,
        provider_activity: ProviderActivity,
        manifests: list[PluginManifest],
    ) -> HostOverlayBuild: ...

    def build_state_monitor(
        self,
        runtime: CoreRuntime,
        overlay: _OverlayLike,
        widget_sources: list[tuple[str, str, str]],
    ) -> HostStateMonitorBuild: ...


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


def boot_runtime(
    paths: AppPaths,
    manifests: list[PluginManifest],
    *,
    host_assembly: HostAssembly,
) -> CoreRuntime:
    """Build and wire the runtime before the Qt event loop starts."""
    total_start = perf_counter()
    assembly = _create_boot_assembly(paths, manifests, host_assembly)
    _run_pre_registry_phases(assembly, _pre_registry_phases(assembly))
    lifecycle = assembly.lifecycle
    overlay_build = assembly.overlay_build
    provider_activity = assembly.provider_activity
    if lifecycle is None or overlay_build is None or provider_activity is None:
        raise RuntimeError("boot assembly is incomplete after required runtime phases")
    _attach_runtime_surfaces(lifecycle, provider_activity)

    extra_context = {
        "widgetModel": overlay_build.overlay.model,
        "widgetOverlayState": overlay_build.overlay.state,
    }
    host_workers = HostWorkerSupervisor()

    registry = build_runtime_registry(
        assembly.runtime,
        lifecycle,
        assembly.process_supervisor,
        provider_activity,
        overlay_build.overlay,
        None,
        devtools_monitor_interval_ms=assembly.host_assembly.devtools_monitor_interval_ms,
        boot_phase_states=assembly.boot_phase_states,
    )
    assembly.process_supervisor.attach_registry(registry)
    lifecycle.attach_runtime_registry(registry)
    provider_activity.attach_runtime_registry(registry)
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
        paths=assembly.paths,
        host=assembly.host,
        runtime=assembly.runtime,
        stop_runtime=assembly.stop_runtime,
        lifecycle=lifecycle,
        process_supervisor=assembly.process_supervisor,
        provider_activity=provider_activity,
        scheduler=assembly.scheduler,
        host_workers=host_workers,
        runtime_inspector=None,
        overlay=overlay_build.overlay,
        state_monitor=None,
        extra_context=extra_context,
        units=registry,
    )
    runtime.runtime_inspector = build_runtime_inspector(
        runtime, overlay_build.widget_sources
    )
    state_monitor_build = cast(
        HostStateMonitorBuild,
        _run_registry_phases(
            runtime,
            assembly.boot_phase_states,
            (
                _RegistryPhaseSpec(
                    name="build_state_monitor",
                    action=lambda: assembly.host_assembly.build_state_monitor(
                        runtime, overlay_build.overlay, overlay_build.widget_sources
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
    return runtime


def _create_boot_assembly(
    paths: AppPaths,
    manifests: list[PluginManifest],
    host_assembly: HostAssembly,
) -> _BootAssembly:
    """Build the early boot assembly inputs before phase orchestration begins."""
    boot_phase_states: dict[str, RuntimeState] = {}
    consumer_manifests = [m for m in manifests if m.is_consumer]
    provider_manifests = [m for m in manifests if m.is_provider]
    process_supervisor = ProcessSupervisor()
    scheduler = RuntimeScheduler()
    phase_start = perf_counter()
    composition = create_runtime_composition(
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
    _log_startup_phase("create_runtime_composition", phase_start)

    return _BootAssembly(
        paths=paths,
        manifests=manifests,
        consumer_manifests=consumer_manifests,
        provider_manifests=provider_manifests,
        boot_phase_states=boot_phase_states,
        process_supervisor=process_supervisor,
        scheduler=scheduler,
        host=composition.host,
        runtime=composition.runtime,
        start_runtime=lambda: composition.start(plugins=False),
        stop_runtime=composition.stop,
        host_assembly=host_assembly,
        provider_activity=ProviderActivity(composition.runtime.session),
    )


def _pre_registry_phases(assembly: _BootAssembly) -> tuple[_PreRegistryPhaseSpec, ...]:
    """Describe pre-registry boot phases as assembly data."""
    return (
        _PreRegistryPhaseSpec(
            name="register_consumers",
            action=lambda: _register_consumers(assembly.host, assembly.runtime),
        ),
        _PreRegistryPhaseSpec(
            name="register_host",
            action=lambda: _register_host_and_start(
                assembly.host,
                assembly.start_runtime,
                assembly.host_assembly,
            ),
        ),
        _PreRegistryPhaseSpec(
            name="activate_plugins",
            action=lambda: _activate_plugins(assembly.runtime, assembly.scheduler),
            assign=lambda result: setattr(assembly, "lifecycle", result),
        ),
        _PreRegistryPhaseSpec(
            name="register_providers",
            action=lambda: _register_providers(
                assembly.runtime,
                assembly.provider_manifests,
                cast(ProviderActivity, assembly.provider_activity),
            ),
        ),
        _PreRegistryPhaseSpec(
            name="bind_consumers",
            action=lambda: _bind_consumers(
                assembly.runtime,
                assembly.consumer_manifests,
                cast(ProviderActivity, assembly.provider_activity),
            ),
        ),
        _PreRegistryPhaseSpec(
            name="build_overlay",
            action=lambda: assembly.host_assembly.build_overlay(
                assembly.paths,
                assembly.host,
                assembly.runtime,
                cast(ProviderActivity, assembly.provider_activity),
                assembly.consumer_manifests,
            ),
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


def _load_host_state(host: HostServices) -> None:
    host.persistence.load_all()


def _register_host_and_start(
    host: HostServices,
    start_runtime: Callable[[], None],
    host_assembly: HostAssembly,
) -> None:
    host_assembly.register_host(host)
    _load_host_state(host)
    start_runtime()


def _register_consumers(host: HostServices, runtime: RuntimeServices) -> None:
    """Run the consumer registration phase explicitly from the runtime boot path."""
    runtime.plugins.register_all(host, runtime)


def _activate_plugins(
    runtime: RuntimeServices,
    scheduler: RuntimeScheduler,
) -> PluginLifecycleManager:
    lifecycle = PluginLifecycleManager(
        runtime.plugins,
        scheduler=scheduler,
        grace_seconds=30.0,
    )
    plugin_names = [p.name for p in runtime.plugins.plugins]
    if plugin_names:
        lifecycle.activate(plugin_names[0])
    return lifecycle


def _attach_runtime_surfaces(
    lifecycle: PluginLifecycleManager,
    provider_activity: ProviderActivity,
) -> None:
    """Attach runtime-owned provider activity to the plugin lifecycle."""
    lifecycle.attach_provider_activity(provider_activity)


def _register_providers(
    runtime: RuntimeServices,
    manifests: list[PluginManifest],
    provider_activity: ProviderActivity,
) -> None:
    for manifest in manifests:
        if manifest.provider is None:
            continue
        provider = manifest.provider.create()
        provider.open()
        runtime.session.register_provider(manifest.name, provider, manifest.exports)
        provider_activity.provider_registered(manifest.name)
        _log.info(
            "provider registered  plugin=%s  type=%s  exports=%s",
            manifest.name,
            type(provider).__name__,
            ", ".join(manifest.exports) if manifest.exports else "-",
        )


def _bind_consumers(
    runtime: RuntimeServices,
    manifests: list[PluginManifest],
    provider_activity: ProviderActivity,
) -> None:
    for manifest in manifests:
        bindings = runtime.session.bind_consumer(
            manifest.name,
            manifest.requires,
            manifest.provider_requests,
        )
        provider_activity.bindings_changed(manifest.name)
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
