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

"""Core-owned runtime vocabulary and top-level runtime shell.

Keep runtime exports lazy so lightweight helpers such as ``unit_ids`` can be
imported without constructing the full runtime boot dependency chain.
"""

from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .boot import boot_runtime, discover_manifests
    from .core_runtime import CoreRuntime, build_runtime_registry
    from .host_workers import HostWorkerHandle, HostWorkerSupervisor
    from .models import (
        RuntimeActivationPolicy,
        RuntimeExecutionPolicy,
        RuntimeState,
        RuntimeTransport,
        RuntimeUnitInfo,
        RuntimeUnitKind,
        RuntimeUnitSpec,
    )
    from .scheduling import RuntimeClock, RuntimeScheduleKind, RuntimeScheduleSpec
    from .process_supervisor import ProcessInfo, ProcessSupervisor, SpawnedProcessHandle
    from .registry import RuntimeRegistry
    from .scheduler import RuntimeScheduler, ScheduledTaskHandle
    from .unit_ids import (
        boot_phase_unit_id,
        plugin_consumer_unit_id,
        plugin_process_unit_id,
        provider_capability_unit_id,
        provider_runtime_unit_id,
    )
    from tinycore.diagnostics.runtime_state import InspectionEntry, InspectionSourceInfo, RuntimeInspector
    from tinycore.diagnostics.snapshot_protocols import InspectionSnapshot, InspectionSnapshotProvider


_EXPORTS: dict[str, tuple[str, str]] = {
    "CoreRuntime": (".core_runtime", "CoreRuntime"),
    "HostWorkerHandle": (".host_workers", "HostWorkerHandle"),
    "HostWorkerSupervisor": (".host_workers", "HostWorkerSupervisor"),
    "InspectionEntry": ("tinycore.diagnostics.runtime_state", "InspectionEntry"),
    "InspectionSnapshot": ("tinycore.diagnostics.snapshot_protocols", "InspectionSnapshot"),
    "InspectionSnapshotProvider": ("tinycore.diagnostics.snapshot_protocols", "InspectionSnapshotProvider"),
    "InspectionSourceInfo": ("tinycore.diagnostics.runtime_state", "InspectionSourceInfo"),
    "ProcessInfo": (".process_supervisor", "ProcessInfo"),
    "ProcessSupervisor": (".process_supervisor", "ProcessSupervisor"),
    "RuntimeActivationPolicy": (".models", "RuntimeActivationPolicy"),
    "RuntimeClock": (".scheduling", "RuntimeClock"),
    "RuntimeExecutionPolicy": (".models", "RuntimeExecutionPolicy"),
    "RuntimeInspector": ("tinycore.diagnostics.runtime_state", "RuntimeInspector"),
    "RuntimeRegistry": (".registry", "RuntimeRegistry"),
    "RuntimeScheduleKind": (".scheduling", "RuntimeScheduleKind"),
    "RuntimeScheduleSpec": (".scheduling", "RuntimeScheduleSpec"),
    "RuntimeScheduler": (".scheduler", "RuntimeScheduler"),
    "RuntimeState": (".models", "RuntimeState"),
    "RuntimeTransport": (".models", "RuntimeTransport"),
    "RuntimeUnitInfo": (".models", "RuntimeUnitInfo"),
    "RuntimeUnitKind": (".models", "RuntimeUnitKind"),
    "RuntimeUnitSpec": (".models", "RuntimeUnitSpec"),
    "SpawnedProcessHandle": (".process_supervisor", "SpawnedProcessHandle"),
    "ScheduledTaskHandle": (".scheduler", "ScheduledTaskHandle"),
    "boot_phase_unit_id": (".unit_ids", "boot_phase_unit_id"),
    "boot_runtime": (".boot", "boot_runtime"),
    "build_runtime_registry": (".core_runtime", "build_runtime_registry"),
    "discover_manifests": (".boot", "discover_manifests"),
    "plugin_consumer_unit_id": (".unit_ids", "plugin_consumer_unit_id"),
    "plugin_process_unit_id": (".unit_ids", "plugin_process_unit_id"),
    "provider_capability_unit_id": (".unit_ids", "provider_capability_unit_id"),
    "provider_runtime_unit_id": (".unit_ids", "provider_runtime_unit_id"),
}

__all__ = (
    "CoreRuntime",
    "HostWorkerHandle",
    "HostWorkerSupervisor",
    "InspectionEntry",
    "InspectionSnapshot",
    "InspectionSnapshotProvider",
    "InspectionSourceInfo",
    "ProcessInfo",
    "ProcessSupervisor",
    "RuntimeActivationPolicy",
    "RuntimeClock",
    "RuntimeExecutionPolicy",
    "RuntimeInspector",
    "RuntimeRegistry",
    "RuntimeScheduleKind",
    "RuntimeScheduleSpec",
    "RuntimeScheduler",
    "RuntimeState",
    "RuntimeTransport",
    "RuntimeUnitInfo",
    "RuntimeUnitKind",
    "RuntimeUnitSpec",
    "SpawnedProcessHandle",
    "ScheduledTaskHandle",
    "boot_phase_unit_id",
    "boot_runtime",
    "build_runtime_registry",
    "discover_manifests",
    "plugin_consumer_unit_id",
    "plugin_process_unit_id",
    "provider_capability_unit_id",
    "provider_runtime_unit_id",
)


def __getattr__(name: str):
    target = _EXPORTS.get(name)
    if target is None:
        raise AttributeError(f"module 'tinycore.runtime' has no attribute '{name}'")
    module_name, attr_name = target
    module = import_module(module_name, __name__) if module_name.startswith(".") else import_module(module_name)
    value = getattr(module, attr_name)
    globals()[name] = value
    return value
