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

"""Registry for runtime-owned units."""

from __future__ import annotations

from .models import RuntimeState, RuntimeUnitInfo, RuntimeUnitSpec


class RuntimeRegistry:
    """Stores declared runtime units and their current state."""

    def __init__(self) -> None:
        self._units: dict[str, RuntimeUnitInfo] = {}

    def declare(self, spec: RuntimeUnitSpec, *, state: RuntimeState = "declared") -> RuntimeUnitInfo:
        """Declare or replace one runtime unit."""
        info = RuntimeUnitInfo(
            id=spec.id,
            kind=spec.kind,
            role=spec.role,
            owner=spec.owner,
            transport=spec.transport,
            state=state,
            parent_id=spec.parent_id,
            pid=spec.pid,
            execution_policy=spec.execution_policy,
            activation_policy=spec.activation_policy,
            start_order=spec.start_order,
            stop_order=spec.stop_order,
            depends_on=spec.depends_on,
            schedule_kind=spec.schedule_kind,
            schedule_clock=spec.schedule_clock,
            schedule_driver=spec.schedule_driver,
            schedule_stage=spec.schedule_stage,
            interval_ms=spec.interval_ms,
            delay_ms=spec.delay_ms,
        )
        self._units[info.id] = info
        return info

    def set_state(self, unit_id: str, state: RuntimeState) -> RuntimeUnitInfo:
        """Update the current lifecycle state of one unit."""
        current = self._units[unit_id]
        updated = RuntimeUnitInfo(
            id=current.id,
            kind=current.kind,
            role=current.role,
            owner=current.owner,
            transport=current.transport,
            state=state,
            parent_id=current.parent_id,
            pid=current.pid,
            execution_policy=current.execution_policy,
            activation_policy=current.activation_policy,
            start_order=current.start_order,
            stop_order=current.stop_order,
            depends_on=current.depends_on,
            schedule_kind=current.schedule_kind,
            schedule_clock=current.schedule_clock,
            schedule_driver=current.schedule_driver,
            schedule_stage=current.schedule_stage,
            interval_ms=current.interval_ms,
            delay_ms=current.delay_ms,
        )
        self._units[unit_id] = updated
        return updated

    def set_pid(self, unit_id: str, pid: int | None) -> RuntimeUnitInfo:
        """Update the PID for one runtime unit."""
        current = self._units[unit_id]
        updated = RuntimeUnitInfo(
            id=current.id,
            kind=current.kind,
            role=current.role,
            owner=current.owner,
            transport=current.transport,
            state=current.state,
            parent_id=current.parent_id,
            pid=pid,
            execution_policy=current.execution_policy,
            activation_policy=current.activation_policy,
            start_order=current.start_order,
            stop_order=current.stop_order,
            depends_on=current.depends_on,
            schedule_kind=current.schedule_kind,
            schedule_clock=current.schedule_clock,
            schedule_driver=current.schedule_driver,
            schedule_stage=current.schedule_stage,
            interval_ms=current.interval_ms,
            delay_ms=current.delay_ms,
        )
        self._units[unit_id] = updated
        return updated

    def get(self, unit_id: str) -> RuntimeUnitInfo | None:
        """Return one runtime unit by id."""
        return self._units.get(unit_id)

    def all(self) -> list[RuntimeUnitInfo]:
        """Return all runtime units in declaration order."""
        return list(self._units.values())

    def start_sorted(self, unit_ids: list[str] | None = None) -> list[RuntimeUnitInfo]:
        """Return units sorted by start order and declaration id."""
        infos = self._select(unit_ids)
        return sorted(infos, key=lambda info: (info.start_order, info.id))

    def stop_sorted(self, unit_ids: list[str] | None = None) -> list[RuntimeUnitInfo]:
        """Return units sorted by stop order descending and declaration id."""
        infos = self._select(unit_ids)
        return sorted(infos, key=lambda info: (info.stop_order, info.id), reverse=True)

    def dependencies_running(self, unit_id: str) -> bool:
        """Return True when all declared dependencies are currently running."""
        unit = self._units.get(unit_id)
        if unit is None:
            return False
        for dependency_id in unit.depends_on:
            dependency = self._units.get(dependency_id)
            if dependency is None or dependency.state != "running":
                return False
        return True

    def dependents_stopped(self, unit_id: str) -> bool:
        """Return True when all dependents are no longer active."""
        for info in self._units.values():
            if unit_id not in info.depends_on:
                continue
            if info.state in {"starting", "running", "stopping"}:
                return False
        return True

    def _select(self, unit_ids: list[str] | None) -> list[RuntimeUnitInfo]:
        if unit_ids is None:
            return list(self._units.values())
        return [self._units[unit_id] for unit_id in unit_ids if unit_id in self._units]
