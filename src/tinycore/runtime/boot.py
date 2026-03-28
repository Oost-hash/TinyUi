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
from tinycore.plugin.manifest import PluginManifest, scan_plugins
from tinycore.services import HostServices, RuntimeServices

from .core_runtime import CoreRuntime, build_runtime_registry
from .host_workers import HostWorkerHandle, HostWorkerSupervisor
from .models import RuntimeState
from .process_supervisor import ProcessSupervisor
from .plugins.activation import PluginActivationManager
from .plugins.participants import (
    PluginParticipant,
    ProviderParticipant,
    bind_plugin_participants,
    build_plugin_participants,
    build_provider_participants,
    register_provider_participants,
)
from .plugins.provider_activity import ProviderActivity
from .scheduler import RuntimeScheduler
from .unit_ids import boot_phase_unit_id

_log = get_logger(__name__)
_T = TypeVar("_T")
_BOOT_PHASE_ORDER = (
    "register_participants",
    "register_host",
    "activate_plugins",
    "register_providers",
    "bind_participants",
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
    extra_context: dict[str, tuple[type, str, object]]


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
    plugin_participants: list[PluginParticipant]
    provider_participants: list[ProviderParticipant]
    boot_phase_states: dict[str, RuntimeState]
    process_supervisor: ProcessSupervisor
    scheduler: RuntimeScheduler
    host: HostServices
    runtime: RuntimeServices
    start_runtime: Callable[[], None]
    stop_runtime: Callable[[], None]
    host_assembly: HostAssembly
    provider_activity: ProviderActivity | None = None
    activation: PluginActivationManager | None = None
    overlay_build: HostOverlayBuild | None = None
    host_worker_build: _HostWorkerBuild | None = None


class _OverlayLike(Protocol):
    @property
    def model(self) -> object: ...

    @property
    def state(self) -> object: ...

    @property
    def extra_context(self) -> dict[str, tuple[type, str, object]]: ...

    @property
    def update_interval_ms(self) -> int: ...

    def update_participants(self) -> tuple[tuple[str, str], ...]: ...

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

    def startup_participant(self, host: HostServices) -> str | None: ...

    def build_overlay(
        self,
        paths: AppPaths,
        host: HostServices,
        runtime: RuntimeServices,
        provider_activity: ProviderActivity,
        participants: list[PluginParticipant],
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
    activation = assembly.activation
    overlay_build = assembly.overlay_build
    provider_activity = assembly.provider_activity
    if activation is None or overlay_build is None or provider_activity is None:
        raise RuntimeError("boot assembly is incomplete after required runtime phases")
    _attach_runtime_surfaces(activation, provider_activity)

    extra_context = dict(overlay_build.overlay.extra_context)
    host_workers = HostWorkerSupervisor()

    registry = build_runtime_registry(
        assembly.runtime,
        activation,
        assembly.process_supervisor,
        provider_activity,
        overlay_build.overlay,
        None,
        devtools_monitor_interval_ms=assembly.host_assembly.devtools_monitor_interval_ms,
        boot_phase_states=assembly.boot_phase_states,
    )
    assembly.process_supervisor.attach_registry(registry)
    activation.attach_runtime_registry(registry)
    provider_activity.attach_runtime_registry(registry)
    host_workers.attach_registry(registry)

    def _start_overlay() -> None:
        overlay_build.overlay.start()
        registry.set_state("ui.widgets.update", "running")

    def _stop_overlay() -> None:
        registry.set_state("ui.widgets.update", "stopping")
        overlay_build.overlay.stop()
        registry.set_state("ui.widgets.update", "stopped")

    assembly.host_worker_build = _build_host_workers(
        activation,
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
        activation=activation,
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

    startup = assembly.host_assembly.startup_participant(assembly.host)
    if startup is not None:
        known = {p.name for p in assembly.runtime.plugin_runtime.registered_participants}
        if startup in known:
            runtime.activation.activate(startup)

    runtime.extra_context.update(state_monitor_build.extra_context)
    if state_monitor_build.state_monitor is not None:
        runtime.state_monitor = state_monitor_build.state_monitor
        assembly.host_worker_build = _build_host_workers(
            activation,
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
    participant_manifests = [m for m in manifests if m.is_consumer]
    process_supervisor = ProcessSupervisor()
    plugin_participants = build_plugin_participants(
        participant_manifests,
        process_supervisor=process_supervisor,
    )
    provider_participants = build_provider_participants(
        [m for m in manifests if m.is_provider]
    )
    scheduler = RuntimeScheduler()
    phase_start = perf_counter()
    composition = create_runtime_composition(
        paths,
        *plugin_participants,
        register_plugins=False,
    )
    _log_startup_phase("create_runtime_composition", phase_start)

    return _BootAssembly(
        paths=paths,
        manifests=manifests,
        plugin_participants=plugin_participants,
        provider_participants=provider_participants,
        boot_phase_states=boot_phase_states,
        process_supervisor=process_supervisor,
        scheduler=scheduler,
        host=composition.host,
        runtime=composition.runtime,
        start_runtime=lambda: None,
        stop_runtime=lambda: None,
        host_assembly=host_assembly,
        provider_activity=ProviderActivity(composition.runtime.plugin_facts),
    )


def _pre_registry_phases(assembly: _BootAssembly) -> tuple[_PreRegistryPhaseSpec, ...]:
    """Describe pre-registry boot phases as assembly data."""
    return (
        _PreRegistryPhaseSpec(
            name="register_participants",
            action=lambda: _register_participants(assembly.host, assembly.runtime),
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
            assign=lambda result: setattr(assembly, "activation", result),
        ),
        _PreRegistryPhaseSpec(
            name="register_providers",
            action=lambda: _register_providers(
                assembly.runtime,
                assembly.provider_participants,
                cast(ProviderActivity, assembly.provider_activity),
            ),
        ),
        _PreRegistryPhaseSpec(
            name="bind_participants",
            action=lambda: _bind_plugin_participants(
                assembly.runtime,
                assembly.plugin_participants,
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
                assembly.plugin_participants,
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


def _register_participants(host: HostServices, runtime: RuntimeServices) -> None:
    """Run the plugin participation registration phase from the runtime boot path."""
    runtime.plugin_runtime.register_participants(host, runtime)


def _activate_plugins(
    runtime: RuntimeServices,
    scheduler: RuntimeScheduler,
) -> PluginActivationManager:
    return PluginActivationManager(
        runtime.plugin_runtime,
        scheduler=scheduler,
        grace_seconds=30.0,
    )


def _attach_runtime_surfaces(
    activation: PluginActivationManager,
    provider_activity: ProviderActivity,
) -> None:
    """Attach runtime-owned provider activity to the plugin activation manager."""
    activation.attach_provider_activity(provider_activity)


def _register_providers(
    runtime: RuntimeServices,
    participants: list[ProviderParticipant],
    provider_activity: ProviderActivity,
) -> None:
    register_provider_participants(runtime, participants, provider_activity)


def _bind_plugin_participants(
    runtime: RuntimeServices,
    participants: list[PluginParticipant],
    provider_activity: ProviderActivity,
) -> None:
    bind_plugin_participants(runtime, participants, provider_activity)


def _build_host_workers(
    activation: PluginActivationManager,
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
            unit_id="runtime.plugins.activation",
            stop=activation.shutdown,
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
