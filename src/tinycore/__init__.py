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
"""tinycore — generic application engine.

Keep package-level imports lazy so submodule imports such as
``from tinycore.paths import AppPaths`` do not eagerly initialize the full app
and runtime graph during bootstrap.
"""

from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .app import App, create_app
    from .logging import LogInspector
    from .paths import AppPaths
    from .persistence import WidgetStateRegistry, WidgetStateStore
    from .plugin.lifecycle import PluginLifecycleManager
    from .plugin.subprocess_host import SubprocessPlugin
    from .runtime import (
        CoreRuntime,
        HostWorkerHandle,
        HostWorkerSupervisor,
        InspectionEntry,
        InspectionSnapshot,
        InspectionSnapshotProvider,
        InspectionSourceInfo,
        ProcessInfo,
        ProcessSupervisor,
        RuntimeActivationPolicy,
        RuntimeClock,
        RuntimeExecutionPolicy,
        RuntimeInspector,
        RuntimeRegistry,
        RuntimeScheduleKind,
        RuntimeScheduleSpec,
        RuntimeScheduler,
        RuntimeUnitInfo,
        RuntimeUnitSpec,
        ScheduledTaskHandle,
        boot_phase_unit_id,
        plugin_consumer_unit_id,
        plugin_process_unit_id,
        provider_capability_unit_id,
        provider_runtime_unit_id,
    )
    from tinyui_schema import SettingsSpec


_EXPORTS: dict[str, tuple[str, str]] = {
    "App": (".app", "App"),
    "AppPaths": (".paths", "AppPaths"),
    "CoreRuntime": (".runtime", "CoreRuntime"),
    "HostWorkerHandle": (".runtime", "HostWorkerHandle"),
    "HostWorkerSupervisor": (".runtime", "HostWorkerSupervisor"),
    "InspectionEntry": (".runtime", "InspectionEntry"),
    "InspectionSnapshot": (".runtime", "InspectionSnapshot"),
    "InspectionSnapshotProvider": (".runtime", "InspectionSnapshotProvider"),
    "InspectionSourceInfo": (".runtime", "InspectionSourceInfo"),
    "LogInspector": (".logging", "LogInspector"),
    "PluginLifecycleManager": (".plugin.lifecycle", "PluginLifecycleManager"),
    "ProcessInfo": (".runtime", "ProcessInfo"),
    "ProcessSupervisor": (".runtime", "ProcessSupervisor"),
    "RuntimeActivationPolicy": (".runtime", "RuntimeActivationPolicy"),
    "RuntimeClock": (".runtime", "RuntimeClock"),
    "RuntimeExecutionPolicy": (".runtime", "RuntimeExecutionPolicy"),
    "RuntimeInspector": (".runtime", "RuntimeInspector"),
    "RuntimeRegistry": (".runtime", "RuntimeRegistry"),
    "RuntimeScheduleKind": (".runtime", "RuntimeScheduleKind"),
    "RuntimeScheduleSpec": (".runtime", "RuntimeScheduleSpec"),
    "RuntimeScheduler": (".runtime", "RuntimeScheduler"),
    "RuntimeUnitInfo": (".runtime", "RuntimeUnitInfo"),
    "RuntimeUnitSpec": (".runtime", "RuntimeUnitSpec"),
    "ScheduledTaskHandle": (".runtime", "ScheduledTaskHandle"),
    "SettingsSpec": ("tinyui_schema", "SettingsSpec"),
    "SubprocessPlugin": (".plugin.subprocess_host", "SubprocessPlugin"),
    "WidgetStateRegistry": (".persistence", "WidgetStateRegistry"),
    "WidgetStateStore": (".persistence", "WidgetStateStore"),
    "boot_phase_unit_id": (".runtime", "boot_phase_unit_id"),
    "create_app": (".app", "create_app"),
    "plugin_consumer_unit_id": (".runtime", "plugin_consumer_unit_id"),
    "plugin_process_unit_id": (".runtime", "plugin_process_unit_id"),
    "provider_capability_unit_id": (".runtime", "provider_capability_unit_id"),
    "provider_runtime_unit_id": (".runtime", "provider_runtime_unit_id"),
}

__all__ = (
    "App",
    "AppPaths",
    "CoreRuntime",
    "HostWorkerHandle",
    "HostWorkerSupervisor",
    "InspectionEntry",
    "InspectionSnapshot",
    "InspectionSnapshotProvider",
    "InspectionSourceInfo",
    "LogInspector",
    "PluginLifecycleManager",
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
    "RuntimeUnitInfo",
    "RuntimeUnitSpec",
    "ScheduledTaskHandle",
    "SettingsSpec",
    "SubprocessPlugin",
    "WidgetStateRegistry",
    "WidgetStateStore",
    "boot_phase_unit_id",
    "create_app",
    "plugin_consumer_unit_id",
    "plugin_process_unit_id",
    "provider_capability_unit_id",
    "provider_runtime_unit_id",
)


def __getattr__(name: str):
    target = _EXPORTS.get(name)
    if target is None:
        raise AttributeError(f"module 'tinycore' has no attribute '{name}'")
    module_name, attr_name = target
    module = import_module(module_name, __name__) if module_name.startswith(".") else import_module(module_name)
    value = getattr(module, attr_name)
    globals()[name] = value
    return value
