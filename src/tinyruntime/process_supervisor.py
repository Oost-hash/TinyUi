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

"""Core-owned supervisor for subprocess-backed runtime units."""

from __future__ import annotations

import multiprocessing as mp
from dataclasses import dataclass
from typing import Any
from typing import Literal

from tinyplugins.spec import ConsumerRuntimeSpec
from .registry import RuntimeRegistry
from .unit_ids import plugin_participant_unit_id, plugin_process_unit_id

ProcessState = Literal["starting", "running", "stopping", "stopped", "failed"]


@dataclass
class SpawnedProcessHandle:
    """Live handle for one subprocess-backed runtime unit."""

    unit_id: str
    plugin_name: str
    process: mp.Process
    conn: Any
    state: ProcessState = "starting"

    @property
    def pid(self) -> int | None:
        return self.process.pid


@dataclass(frozen=True)
class ProcessInfo:
    """Snapshot metadata for one supervised subprocess."""

    unit_id: str
    plugin_name: str
    pid: int | None
    state: ProcessState


class ProcessSupervisor:
    """Spawn and supervise subprocess-backed runtime units."""

    def __init__(self) -> None:
        self._handles: dict[str, SpawnedProcessHandle] = {}
        self._registry: RuntimeRegistry | None = None

    def attach_registry(self, registry: RuntimeRegistry) -> None:
        """Attach the runtime registry so process state updates become visible."""
        self._registry = registry
        for handle in self._handles.values():
            if registry.get(handle.unit_id) is None:
                continue
            registry.set_pid(handle.unit_id, handle.pid)
            registry.set_state(handle.unit_id, handle.state)

    def spawn_plugin_subprocess(
        self,
        spec: ConsumerRuntimeSpec,
        *,
        extra_paths: list[str],
    ) -> SpawnedProcessHandle:
        """Create the subprocess and return the live transport handle."""
        from tinyruntime.plugins import subprocess_entry

        unit_id = plugin_process_unit_id(spec.name)
        if self._registry is not None:
            info = self._registry.get(unit_id)
            if info is not None:
                if info.execution_policy != "subprocess":
                    raise RuntimeError(
                        f"runtime unit '{unit_id}' cannot spawn as subprocess; "
                        f"policy is '{info.execution_policy}'"
                    )
                if info.activation_policy not in {"warm", "on_demand"}:
                    raise RuntimeError(
                        f"runtime unit '{unit_id}' cannot spawn on demand; "
                        f"activation policy is '{info.activation_policy}'"
                    )
                if info.transport != "subprocess" or info.kind != "process":
                    raise RuntimeError(
                        f"runtime unit '{unit_id}' is not declared as a subprocess process unit"
                    )

        parent_conn, child_conn = mp.Pipe(duplex=True)
        process = mp.Process(
            target=subprocess_entry.run,
            args=(
                child_conn,
                spec.module,
                spec.cls,
                spec.requires,
                spec.artifact_path,
                extra_paths,
            ),
            daemon=True,
            name=f"plugin-{spec.name}",
        )
        process.start()
        child_conn.close()

        handle = SpawnedProcessHandle(
            unit_id=unit_id,
            plugin_name=spec.name,
            process=process,
            conn=parent_conn,
        )
        self._handles[handle.unit_id] = handle
        if self._registry is not None and self._registry.get(handle.unit_id) is not None:
            self._registry.set_pid(handle.unit_id, handle.pid)
            self._registry.set_state(handle.unit_id, "starting")
        return handle

    def mark_running(self, unit_id: str) -> None:
        """Mark a supervised subprocess as running."""
        self._handles[unit_id].state = "running"
        if self._registry is not None and self._registry.get(unit_id) is not None:
            self._registry.set_pid(unit_id, self._handles[unit_id].pid)
            self._registry.set_state(unit_id, "running")

    def mark_failed(self, unit_id: str) -> None:
        """Mark a supervised subprocess as failed."""
        self._handles[unit_id].state = "failed"
        if self._registry is not None and self._registry.get(unit_id) is not None:
            self._registry.set_state(unit_id, "failed")
        self._sync_participant_state(unit_id, "failed")

    def stop(self, handle: SpawnedProcessHandle, *, timeout: float = 5.0) -> None:
        """Stop and reap one supervised subprocess."""
        handle.state = "stopping"  # keep local truth during join/terminate
        if self._registry is not None and self._registry.get(handle.unit_id) is not None:
            self._registry.set_state(handle.unit_id, "stopping")
        self._sync_participant_state(handle.unit_id, "stopping")
        process = handle.process
        process.join(timeout=timeout)
        if process.is_alive():
            process.terminate()
        handle.conn.close()
        handle.state = "stopped"
        if self._registry is not None and self._registry.get(handle.unit_id) is not None:
            self._registry.set_state(handle.unit_id, "stopped")
        self._sync_participant_state(handle.unit_id, "stopped")

    def pid_for_plugin(self, plugin_name: str) -> int | None:
        """Return the current PID for one plugin-backed subprocess."""
        handle = self._handles.get(plugin_process_unit_id(plugin_name))
        return handle.pid if handle is not None else None

    def infos(self) -> list[ProcessInfo]:
        """Return snapshot metadata for all supervised subprocesses."""
        return [
            ProcessInfo(
                unit_id=handle.unit_id,
                plugin_name=handle.plugin_name,
                pid=handle.pid,
                state=handle.state,
            )
            for handle in self._handles.values()
        ]

    def _sync_participant_state(self, unit_id: str, state: ProcessState) -> None:
        if self._registry is None:
            return
        plugin_name = unit_id.removeprefix("plugin.process:")
        participant_unit_id = plugin_participant_unit_id(plugin_name)
        if self._registry.get(participant_unit_id) is None:
            return
        self._registry.set_state(participant_unit_id, state)
