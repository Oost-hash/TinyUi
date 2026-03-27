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

"""Top-level runtime owner for the current TinyUi process graph."""

from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Callable, Protocol

from tinycore.diagnostics.runtime_state import RuntimeInspector
from tinycore.paths import AppPaths
from tinycore.services import HostServices, RuntimeServices

from .host_workers import HostWorkerSupervisor
from .models import RuntimeActivationPolicy, RuntimeExecutionPolicy, RuntimeState, RuntimeUnitInfo, RuntimeUnitSpec
from .plugins.lifecycle import PluginActivationManager
from .provider_activity import ProviderActivity
from .process_supervisor import ProcessSupervisor
from .registry import RuntimeRegistry
from .scheduler import RuntimeScheduler
from .unit_ids import (
    boot_phase_unit_id,
    plugin_participant_unit_id,
    plugin_process_unit_id,
    provider_export_unit_id,
    provider_runtime_unit_id,
)


class _OverlayLike(Protocol):
    @property
    def update_interval_ms(self) -> int: ...

    def start(self) -> None: ...
    def stop(self) -> None: ...


class _StateMonitorLike(Protocol):
    @property
    def refresh_interval_ms(self) -> int: ...

    def start(self) -> None: ...
    def shutdown(self) -> None: ...


@dataclass
class CoreRuntime:
    """Core-owned runtime shell around the current host/runtime composition."""

    paths: AppPaths
    host: HostServices
    runtime: RuntimeServices
    stop_runtime: Callable[[], None]
    lifecycle: PluginActivationManager
    process_supervisor: ProcessSupervisor
    provider_activity: ProviderActivity
    scheduler: RuntimeScheduler
    host_workers: HostWorkerSupervisor
    runtime_inspector: RuntimeInspector | None
    overlay: _OverlayLike
    state_monitor: _StateMonitorLike | None
    extra_context: dict[str, object]
    units: RuntimeRegistry

    def start_host_workers(self) -> None:
        """Start core-owned host workers whose activation policy is always-on."""
        self.host_workers.start_autostart_workers()

    def activate_host_unit(self, unit_id: str) -> None:
        """Activate one host-backed runtime unit through the core-owned runtime API."""
        info = self.units.get(unit_id)
        if info is None:
            raise KeyError(f"Runtime unit '{unit_id}' is not declared")
        if info.execution_policy != "host":
            raise RuntimeError(
                f"runtime unit '{unit_id}' is not host-backed; execution policy is '{info.execution_policy}'"
            )
        if info.activation_policy not in {"always", "warm", "on_demand"}:
            raise RuntimeError(
                f"runtime unit '{unit_id}' cannot be activated through the host runtime API; "
                f"activation policy is '{info.activation_policy}'"
            )
        self.host_workers.start(unit_id)

    def deactivate_host_unit(self, unit_id: str) -> None:
        """Deactivate one host-backed runtime unit through the core-owned runtime API."""
        info = self.units.get(unit_id)
        if info is None:
            raise KeyError(f"Runtime unit '{unit_id}' is not declared")
        if info.execution_policy != "host":
            raise RuntimeError(
                f"runtime unit '{unit_id}' is not host-backed; execution policy is '{info.execution_policy}'"
            )
        if info.activation_policy not in {"warm", "on_demand"}:
            raise RuntimeError(
                f"runtime unit '{unit_id}' cannot be deactivated through the host runtime API; "
                f"activation policy is '{info.activation_policy}'"
            )
        self.host_workers.stop(unit_id)

    def shutdown(self) -> None:
        """Shut down host workers and then stop the wrapped runtime composition."""
        self.host_workers.shutdown()
        self.scheduler.shutdown()
        self.stop_runtime()

    def unit_infos(self) -> list[RuntimeUnitInfo]:
        """Expose declared runtime units for diagnostics and future supervision."""
        return self.units.all()

    def scheduled_task_ids(self) -> tuple[str, ...]:
        """Expose currently scheduled delayed runtime tasks."""
        return self.scheduler.task_ids()

    def unit_execution_policy(self, unit_id: str) -> RuntimeExecutionPolicy | None:
        """Return the declared execution policy for one runtime unit."""
        info = self.units.get(unit_id)
        return info.execution_policy if info is not None else None

    def unit_activation_policy(self, unit_id: str) -> RuntimeActivationPolicy | None:
        """Return the declared activation policy for one runtime unit."""
        info = self.units.get(unit_id)
        return info.activation_policy if info is not None else None


def build_runtime_registry(
    runtime: RuntimeServices,
    lifecycle: PluginActivationManager,
    process_supervisor: ProcessSupervisor,
    provider_activity: ProviderActivity,
    overlay: _OverlayLike,
    state_monitor: _StateMonitorLike | None,
    *,
    devtools_monitor_interval_ms: int | None = None,
    boot_phase_states: dict[str, RuntimeState] | None = None,
) -> RuntimeRegistry:
    """Build the initial runtime graph for the current process arrangement."""
    registry = RuntimeRegistry()
    host_pid = os.getpid()

    def _boot_state(phase_name: str) -> RuntimeState:
        if boot_phase_states is None:
            return "declared"
        return boot_phase_states.get(boot_phase_unit_id(phase_name), "declared")

    registry.declare(
        RuntimeUnitSpec(
            id="host.main",
            kind="process",
            role="host.main",
            owner="tinycore.runtime",
            transport="host",
            pid=host_pid,
            execution_policy="host",
            activation_policy="always",
            start_order=0,
            stop_order=1000,
            schedule_kind="manual",
            schedule_clock="host",
            schedule_driver="runtime.host",
        ),
        state="running",
    )
    registry.declare(
        RuntimeUnitSpec(
            id="runtime.process_supervisor",
            kind="worker",
            role="runtime.process_supervisor",
            owner="tinycore.runtime",
            transport="host",
            parent_id="host.main",
            pid=host_pid,
            execution_policy="host",
            activation_policy="always",
            start_order=10,
            stop_order=990,
            depends_on=("host.main",),
            schedule_kind="manual",
            schedule_clock="host",
            schedule_driver="runtime.process_supervisor",
        ),
        state="running",
    )
    registry.declare(
        RuntimeUnitSpec(
            id="runtime.scheduler",
            kind="worker",
            role="runtime.scheduler",
            owner="tinycore.runtime",
            transport="thread",
            parent_id="host.main",
            pid=host_pid,
            execution_policy="host",
            activation_policy="always",
            start_order=15,
            stop_order=985,
            depends_on=("host.main",),
            schedule_kind="manual",
            schedule_clock="host",
            schedule_driver="runtime.scheduler",
        ),
        state="running",
    )
    registry.declare(
        RuntimeUnitSpec(
            id="runtime.host_workers",
            kind="worker",
            role="runtime.host_workers",
            owner="tinycore.runtime",
            transport="host",
            parent_id="host.main",
            pid=host_pid,
            execution_policy="host",
            activation_policy="always",
            start_order=20,
            stop_order=980,
            depends_on=("host.main",),
            schedule_kind="manual",
            schedule_clock="host",
            schedule_driver="runtime.host_workers",
        ),
        state="running",
    )
    registry.declare(
        RuntimeUnitSpec(
            id=boot_phase_unit_id("register_consumers"),
            kind="adapter",
            role="boot.register_consumers",
            owner="tinycore.runtime",
            transport="host",
            parent_id="host.main",
            pid=host_pid,
            execution_policy="host",
            activation_policy="boot",
            start_order=30,
            stop_order=970,
            depends_on=("host.main",),
            schedule_kind="oneshot",
            schedule_clock="host",
            schedule_driver="runtime.boot",
        ),
        state=_boot_state("register_consumers"),
    )
    registry.declare(
        RuntimeUnitSpec(
            id=boot_phase_unit_id("register_host"),
            kind="adapter",
            role="boot.register_host",
            owner="tinycore.runtime",
            transport="host",
            parent_id="host.main",
            pid=host_pid,
            execution_policy="host",
            activation_policy="boot",
            start_order=40,
            stop_order=960,
            depends_on=("host.main",),
            schedule_kind="oneshot",
            schedule_clock="host",
            schedule_driver="runtime.boot",
        ),
        state=_boot_state("register_host"),
    )
    registry.declare(
        RuntimeUnitSpec(
            id=boot_phase_unit_id("activate_plugins"),
            kind="adapter",
            role="boot.activate_plugins",
            owner="tinycore.runtime",
            transport="host",
            parent_id="host.main",
            pid=host_pid,
            execution_policy="host",
            activation_policy="boot",
            start_order=45,
            stop_order=955,
            depends_on=("host.main",),
            schedule_kind="oneshot",
            schedule_clock="host",
            schedule_driver="runtime.boot",
        ),
        state=_boot_state("activate_plugins"),
    )
    registry.declare(
        RuntimeUnitSpec(
            id=boot_phase_unit_id("register_providers"),
            kind="adapter",
            role="boot.register_providers",
            owner="tinycore.runtime",
            transport="host",
            parent_id="host.main",
            pid=host_pid,
            execution_policy="host",
            activation_policy="boot",
            start_order=50,
            stop_order=950,
            depends_on=("host.main",),
            schedule_kind="oneshot",
            schedule_clock="host",
            schedule_driver="runtime.boot",
        ),
        state=_boot_state("register_providers"),
    )
    registry.declare(
        RuntimeUnitSpec(
            id=boot_phase_unit_id("bind_consumers"),
            kind="adapter",
            role="boot.bind_consumers",
            owner="tinycore.runtime",
            transport="host",
            parent_id="host.main",
            pid=host_pid,
            execution_policy="host",
            activation_policy="boot",
            start_order=60,
            stop_order=940,
            depends_on=("host.main",),
            schedule_kind="oneshot",
            schedule_clock="host",
            schedule_driver="runtime.boot",
        ),
        state=_boot_state("bind_consumers"),
    )
    registry.declare(
        RuntimeUnitSpec(
            id=boot_phase_unit_id("build_overlay"),
            kind="adapter",
            role="boot.build_overlay",
            owner="tinycore.runtime",
            transport="host",
            parent_id="host.main",
            pid=host_pid,
            execution_policy="host",
            activation_policy="boot",
            start_order=70,
            stop_order=930,
            depends_on=("host.main",),
            schedule_kind="oneshot",
            schedule_clock="host",
            schedule_driver="runtime.boot",
        ),
        state=_boot_state("build_overlay"),
    )
    registry.declare(
        RuntimeUnitSpec(
            id=boot_phase_unit_id("build_state_monitor"),
            kind="adapter",
            role="boot.build_state_monitor",
            owner="tinycore.runtime",
            transport="host",
            parent_id="host.main",
            pid=host_pid,
            execution_policy="host",
            activation_policy="boot",
            start_order=80,
            stop_order=920,
            depends_on=("host.main",),
            schedule_kind="oneshot",
            schedule_clock="host",
            schedule_driver="runtime.boot",
        ),
        state=_boot_state("build_state_monitor"),
    )
    registry.declare(
        RuntimeUnitSpec(
            id="ui.main",
            kind="adapter",
            role="ui.main",
            owner="tinyui",
            transport="host",
            parent_id="host.main",
            pid=host_pid,
            execution_policy="host",
            activation_policy="always",
            start_order=100,
            stop_order=900,
            depends_on=("host.main",),
            schedule_kind="manual",
            schedule_clock="host",
            schedule_driver="tinyui.launch",
        )
    )
    registry.declare(
        RuntimeUnitSpec(
            id="ui.widgets.overlay",
            kind="worker",
            role="ui.widgets",
            owner="tinywidgets",
            transport="host",
            parent_id="host.main",
            pid=host_pid,
            execution_policy="host",
            activation_policy="always",
            start_order=200,
            stop_order=800,
            depends_on=("ui.main",),
            schedule_kind="manual",
            schedule_clock="host",
            schedule_driver="runtime.host_workers",
        )
    )
    registry.declare(
        RuntimeUnitSpec(
            id="ui.widgets.update",
            kind="timer",
            role="ui.widgets.update",
            owner="tinywidgets",
            transport="qt_timer",
            parent_id="ui.widgets.overlay",
            pid=host_pid,
            execution_policy="host",
            activation_policy="always",
            start_order=210,
            stop_order=790,
            depends_on=("ui.widgets.overlay",),
            schedule_kind="interval",
            schedule_clock="qt",
            schedule_driver="runtime.qt_timer",
            interval_ms=overlay.update_interval_ms,
        )
    )
    registry.declare(
        RuntimeUnitSpec(
            id="runtime.plugins.activation",
            kind="timer",
            role="runtime.plugins.activation",
            owner="tinycore.runtime.plugins",
            transport="thread",
            parent_id="host.main",
            pid=host_pid,
            execution_policy="thread",
            activation_policy="warm",
            start_order=300,
            stop_order=700,
            depends_on=("host.main",),
            schedule_kind="grace",
            schedule_clock="thread",
            schedule_driver="runtime.scheduler",
            delay_ms=lifecycle.grace_period_ms,
        )
    )

    monitor_interval_ms = (
        state_monitor.refresh_interval_ms
        if state_monitor is not None
        else devtools_monitor_interval_ms
    )
    if monitor_interval_ms is not None:
        registry.declare(
            RuntimeUnitSpec(
                id="devtools.monitor",
                kind="timer",
                role="devtools.monitor",
                owner="tinydevtools",
                transport="qt_timer",
                parent_id="host.main",
                pid=host_pid,
                execution_policy="host",
                activation_policy="on_demand",
                start_order=220,
                stop_order=780,
                depends_on=("ui.widgets.overlay",),
                schedule_kind="interval",
                schedule_clock="qt",
                schedule_driver="runtime.qt_timer",
                interval_ms=monitor_interval_ms,
            )
        )

    for provider in runtime.plugin_facts.providers():
        runtime_unit_id = provider_runtime_unit_id(provider.name)
        provider_state: RuntimeState = (
            "running" if provider.name in provider_activity.active_provider_names() else "idle"
        )
        registry.declare(
            RuntimeUnitSpec(
                id=runtime_unit_id,
                kind="worker",
                role="provider.runtime",
                owner="tinycore.runtime.plugins",
                transport="host",
                parent_id="host.main",
                pid=host_pid,
                execution_policy="host",
                activation_policy="always",
                start_order=150,
                stop_order=850,
                depends_on=("host.main",),
                schedule_kind="manual",
                schedule_clock="host",
                schedule_driver="tinycore.runtime.plugins.provider",
            ),
            state=provider_state,
        )
        for capability in provider.exports:
            registry.declare(
                RuntimeUnitSpec(
                    id=provider_export_unit_id(provider.name, capability),
                    kind="surface",
                    role="provider.export",
                    owner="tinycore.runtime.plugins",
                    transport="host",
                    parent_id=runtime_unit_id,
                    pid=host_pid,
                    execution_policy="host",
                    activation_policy="always",
                    start_order=155,
                    stop_order=845,
                    depends_on=(runtime_unit_id,),
                    schedule_kind="manual",
                    schedule_clock="host",
                    schedule_driver="tinycore.runtime.plugins.provider",
                ),
                state=provider_state,
            )

    supervised_infos = {info.plugin_name: info for info in process_supervisor.infos()}
    active_participants = set(lifecycle.active_participant_names())
    for participant in runtime.plugin_runtime.participants:
        process_info = supervised_infos.get(participant.name)
        pid = process_info.pid if process_info is not None else None
        process_state = process_info.state if process_info is not None else "declared"
        process_unit_id = plugin_process_unit_id(participant.name)
        participant_unit_id = plugin_participant_unit_id(participant.name)

        if pid is not None:
            registry.declare(
                RuntimeUnitSpec(
                    id=process_unit_id,
                    kind="process",
                    role="plugin.process",
                    owner="tinycore.runtime",
                    transport="subprocess",
                    parent_id="host.main",
                    pid=pid,
                    execution_policy="subprocess",
                    activation_policy="warm",
                    start_order=140,
                    stop_order=860,
                    depends_on=("runtime.process_supervisor",),
                    schedule_kind="manual",
                    schedule_clock="host",
                    schedule_driver="runtime.process_supervisor",
                )
            )
        if process_state == "failed":
            participant_state = "failed"
        elif participant.name in active_participants:
            participant_state = "running"
        else:
            participant_state = "idle"

        registry.declare(
            RuntimeUnitSpec(
                id=participant_unit_id,
                kind="adapter",
                role="plugin.participant",
                owner="tinycore.runtime.plugins",
                transport="host",
                parent_id=process_unit_id if pid is not None else "host.main",
                pid=host_pid,
                execution_policy="host",
                activation_policy="warm",
                start_order=160,
                stop_order=840,
                depends_on=((process_unit_id,) if pid is not None else ("host.main",)),
                schedule_kind="manual",
                schedule_clock="host",
                schedule_driver="tinycore.runtime.plugins.activation",
            ),
            state=participant_state,
        )

    return registry
