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

"""Core-owned supervision for host-side runtime workers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .registry import RuntimeRegistry


@dataclass(frozen=True)
class HostWorkerHandle:
    """Registered host-side worker callbacks."""

    unit_id: str
    start: Callable[[], None] | None = None
    stop: Callable[[], None] | None = None


class HostWorkerSupervisor:
    """Register and coordinate host-side runtime workers."""

    def __init__(self) -> None:
        self._workers: list[HostWorkerHandle] = []
        self._started_units: set[str] = set()
        self._registry: RuntimeRegistry | None = None

    def attach_registry(self, registry: RuntimeRegistry) -> None:
        """Attach the runtime registry so worker lifecycle updates become visible."""
        self._registry = registry
        for unit_id in self._started_units:
            if registry.get(unit_id) is not None:
                registry.set_state(unit_id, "running")

    def register(
        self,
        unit_id: str,
        *,
        start: Callable[[], None] | None = None,
        stop: Callable[[], None] | None = None,
    ) -> None:
        """Register one host-side worker."""
        self._workers = [worker for worker in self._workers if worker.unit_id != unit_id]
        self._workers.append(
            HostWorkerHandle(
                unit_id=unit_id,
                start=start,
                stop=stop,
            )
        )

    def start_autostart_workers(self) -> None:
        """Start host workers whose activation policy says they should be always-on."""
        unit_ids = self._autostart_unit_ids()
        for unit_id in self._start_order(unit_ids):
            self.start(unit_id)

    def start(self, unit_id: str) -> None:
        """Start one registered worker if it is not already running."""
        worker = self._worker(unit_id)
        if worker is None or worker.unit_id in self._started_units:
            return
        if self._registry is not None:
            info = self._registry.get(worker.unit_id)
            if info is not None and info.activation_policy == "boot":
                raise RuntimeError(f"boot-only runtime unit '{worker.unit_id}' cannot be started as a host worker")
        if self._registry is not None and not self._registry.dependencies_running(worker.unit_id):
            missing = self._missing_dependencies(worker.unit_id)
            raise RuntimeError(
                f"cannot start runtime unit '{worker.unit_id}' before dependencies are running: {missing}"
            )
        if self._registry is not None and self._registry.get(worker.unit_id) is not None:
            self._registry.set_state(worker.unit_id, "starting")
        if worker.start is not None:
            worker.start()
        self._started_units.add(worker.unit_id)
        if self._registry is not None and self._registry.get(worker.unit_id) is not None:
            self._registry.set_state(worker.unit_id, "running")

    def shutdown(self) -> None:
        """Stop all started workers in reverse registration order."""
        for worker in self._stop_order():
            self.stop(worker.unit_id)

    def stop(self, unit_id: str) -> None:
        """Stop one registered worker if it is currently running."""
        worker = self._worker(unit_id)
        if worker is None or worker.unit_id not in self._started_units:
            return
        if self._registry is not None and self._active_worker_dependents(worker.unit_id):
            raise RuntimeError(
                f"cannot stop runtime unit '{worker.unit_id}' while dependents are still active"
            )
        if self._registry is not None and self._registry.get(worker.unit_id) is not None:
            self._registry.set_state(worker.unit_id, "stopping")
        if worker.stop is not None:
            worker.stop()
        self._started_units.discard(worker.unit_id)
        if self._registry is not None and self._registry.get(worker.unit_id) is not None:
            self._registry.set_state(worker.unit_id, "stopped")

    def _worker(self, unit_id: str) -> HostWorkerHandle | None:
        for worker in self._workers:
            if worker.unit_id == unit_id:
                return worker
        return None

    def _start_order(self, unit_ids: list[str]) -> list[str]:
        if self._registry is None:
            return sorted(unit_ids)
        return [info.id for info in self._registry.start_sorted(unit_ids)]

    def _stop_order(self) -> list[HostWorkerHandle]:
        if self._registry is None:
            return list(reversed(self._workers))

        handles = {worker.unit_id: worker for worker in self._workers}
        ordered: list[HostWorkerHandle] = []
        remaining = set(handles)

        for _ in range(len(handles)):
            progressed = False
            for info in self._registry.stop_sorted(list(remaining)):
                if not self._registry.dependents_stopped(info.id):
                    continue
                ordered.append(handles[info.id])
                remaining.discard(info.id)
                progressed = True
            if not remaining or progressed:
                continue
            for unit_id in sorted(remaining):
                ordered.append(handles[unit_id])
            break

        return ordered

    def _missing_dependencies(self, unit_id: str) -> str:
        if self._registry is None:
            return "-"
        info = self._registry.get(unit_id)
        if info is None or not info.depends_on:
            return "-"
        missing = [
            dependency_id
            for dependency_id in info.depends_on
            if (dependency := self._registry.get(dependency_id)) is None or dependency.state != "running"
        ]
        return ", ".join(missing) if missing else "-"

    def _active_worker_dependents(self, unit_id: str) -> list[str]:
        if self._registry is None:
            return []
        active_workers = self._started_units - {unit_id}
        dependents: list[str] = []
        for dependent_id in active_workers:
            info = self._registry.get(dependent_id)
            if info is None or unit_id not in info.depends_on:
                continue
            if info.state in {"starting", "running", "stopping"}:
                dependents.append(dependent_id)
        return dependents

    def _autostart_unit_ids(self) -> list[str]:
        if self._registry is None:
            return []
        unit_ids: list[str] = []
        for worker in self._workers:
            info = self._registry.get(worker.unit_id)
            if info is not None and info.activation_policy == "always":
                unit_ids.append(worker.unit_id)
        return unit_ids
