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

"""Thin Qt adapter for the core runtime graph."""

from __future__ import annotations

from collections import Counter

from PySide6.QtCore import Property, QObject, Signal, Slot
from PySide6.QtGui import QGuiApplication

from tinycore.runtime.core_runtime import CoreRuntime
from tinycore.runtime.qt_timer import RuntimeQtTimer


class RuntimeViewModel(QObject):
    """Expose runtime units and scheduled tasks to QML."""

    REFRESH_INTERVAL_MS = 400

    unitsChanged = Signal()
    tasksChanged = Signal()
    summaryChanged = Signal()

    def __init__(self, core: CoreRuntime, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._core = core
        self._units: list[dict[str, object]] = []
        self._tasks: list[str] = []
        self._summary = ""
        self._timer = RuntimeQtTimer(
            interval_ms=self.REFRESH_INTERVAL_MS,
            callback=self._refresh,
            parent=self,
        )
        self._refresh()

    @property
    def refresh_interval_ms(self) -> int:
        return self.REFRESH_INTERVAL_MS

    def start(self) -> None:
        self._timer.start()

    def shutdown(self) -> None:
        self._timer.stop()

    def _refresh(self) -> None:
        units: list[dict[str, object]] = [
            {
                "id": unit.id,
                "role": unit.role,
                "kind": unit.kind,
                "owner": unit.owner,
                "state": unit.state,
                "activation": unit.activation_policy,
                "execution": unit.execution_policy,
                "transport": unit.transport,
                "driver": unit.schedule_driver or "",
                "schedule": unit.schedule_kind,
                "clock": unit.schedule_clock,
                "intervalMs": "" if unit.interval_ms is None else str(unit.interval_ms),
                "delayMs": "" if unit.delay_ms is None else str(unit.delay_ms),
                "pid": "" if unit.pid is None else str(unit.pid),
                "parent": unit.parent_id or "",
            }
            for unit in self._core.unit_infos()
        ]
        tasks = list(self._core.scheduled_task_ids())
        counts = Counter(unit["state"] for unit in units)
        summary = (
            f"units={len(units)}  "
            f"running={counts.get('running', 0)}  "
            f"idle={counts.get('idle', 0)}  "
            f"stopped={counts.get('stopped', 0)}  "
            f"failed={counts.get('failed', 0)}  "
            f"tasks={len(tasks)}"
        )

        if units != self._units:
            self._units = units
            self.unitsChanged.emit()
        if tasks != self._tasks:
            self._tasks = tasks
            self.tasksChanged.emit()
        if summary != self._summary:
            self._summary = summary
            self.summaryChanged.emit()

    @Slot()
    def copyOverview(self) -> None:
        clipboard = QGuiApplication.clipboard()
        if clipboard is None:
            return
        clipboard.setText(self._render_overview())

    def _render_overview(self) -> str:
        lines = [
            "Runtime Overview",
            self._summary or "units=0  running=0  idle=0  stopped=0  failed=0  tasks=0",
            "",
        ]
        if self._tasks:
            lines.append("Tasks")
            lines.extend(f"- {task_id}" for task_id in self._tasks)
            lines.append("")

        lines.append("Units")
        if not self._units:
            lines.append("- none")
            return "\n".join(lines)

        for unit in self._units:
            details = [
                f"state={unit['state']}",
                f"kind={unit['kind']}",
                f"execution={unit['execution']}",
                f"activation={unit['activation']}",
            ]
            if unit["owner"]:
                details.append(f"owner={unit['owner']}")
            if unit["transport"]:
                details.append(f"transport={unit['transport']}")
            if unit["driver"]:
                details.append(f"driver={unit['driver']}")
            if unit["schedule"]:
                details.append(f"schedule={unit['schedule']}")
            if unit["clock"]:
                details.append(f"clock={unit['clock']}")
            if unit["intervalMs"]:
                details.append(f"intervalMs={unit['intervalMs']}")
            if unit["delayMs"]:
                details.append(f"delayMs={unit['delayMs']}")
            if unit["pid"]:
                details.append(f"pid={unit['pid']}")
            if unit["parent"]:
                details.append(f"parent={unit['parent']}")
            lines.append(f"- {unit['id']} :: " + "  ".join(details))
        return "\n".join(lines)

    @Property(list, notify=unitsChanged)
    def units(self) -> list[dict[str, object]]:
        return self._units

    @Property(list, notify=tasksChanged)
    def taskIds(self) -> list[str]:
        return self._tasks

    @Property(str, notify=summaryChanged)
    def summary(self) -> str:
        return self._summary
