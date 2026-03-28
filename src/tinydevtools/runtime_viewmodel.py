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
from dataclasses import dataclass

from PySide6.QtCore import (
    Property,
    QAbstractListModel,
    QByteArray,
    QModelIndex,
    QObject,
    QPersistentModelIndex,
    Qt,
    Signal,
    Slot,
)
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QmlElement, QmlSingleton

from tinycore.runtime.core_runtime import CoreRuntime

QML_IMPORT_NAME = "TinyDevTools"
QML_IMPORT_MAJOR_VERSION = 1
from tinycore.runtime.qt_timer import RuntimeQtTimer


@dataclass(frozen=True)
class _RuntimeRow:
    id: str
    display_id: str
    role: str
    kind: str
    owner: str
    state: str
    activation: str
    execution: str
    transport: str
    driver: str
    stage: str
    schedule: str
    clock: str
    interval_ms: str
    delay_ms: str
    pid: str
    parent: str
    depth: int
    has_children: bool
    expanded: bool


class _RuntimeRowsModel(QAbstractListModel):
    IdRole = int(Qt.ItemDataRole.UserRole) + 1
    DisplayIdRole = int(Qt.ItemDataRole.UserRole) + 2
    RoleRole = int(Qt.ItemDataRole.UserRole) + 3
    KindRole = int(Qt.ItemDataRole.UserRole) + 4
    OwnerRole = int(Qt.ItemDataRole.UserRole) + 5
    StateRole = int(Qt.ItemDataRole.UserRole) + 6
    ActivationRole = int(Qt.ItemDataRole.UserRole) + 7
    ExecutionRole = int(Qt.ItemDataRole.UserRole) + 8
    TransportRole = int(Qt.ItemDataRole.UserRole) + 9
    DriverRole = int(Qt.ItemDataRole.UserRole) + 10
    StageRole = int(Qt.ItemDataRole.UserRole) + 11
    ScheduleRole = int(Qt.ItemDataRole.UserRole) + 12
    ClockRole = int(Qt.ItemDataRole.UserRole) + 13
    IntervalMsRole = int(Qt.ItemDataRole.UserRole) + 14
    DelayMsRole = int(Qt.ItemDataRole.UserRole) + 15
    PidRole = int(Qt.ItemDataRole.UserRole) + 16
    ParentRole = int(Qt.ItemDataRole.UserRole) + 17
    DepthRole = int(Qt.ItemDataRole.UserRole) + 18
    HasChildrenRole = int(Qt.ItemDataRole.UserRole) + 19
    ExpandedRole = int(Qt.ItemDataRole.UserRole) + 20

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._rows: list[_RuntimeRow] = []

    def rowCount(
        self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()
    ) -> int:
        return 0 if parent.isValid() else len(self._rows)

    def data(
        self,
        index: QModelIndex | QPersistentModelIndex,
        role: int = int(Qt.ItemDataRole.DisplayRole),
    ):
        if not index.isValid() or not (0 <= index.row() < len(self._rows)):
            return None
        row = self._rows[index.row()]
        if role == self.IdRole:
            return row.id
        if role == self.DisplayIdRole:
            return row.display_id
        if role == self.RoleRole:
            return row.role
        if role == self.KindRole:
            return row.kind
        if role == self.OwnerRole:
            return row.owner
        if role == self.StateRole:
            return row.state
        if role == self.ActivationRole:
            return row.activation
        if role == self.ExecutionRole:
            return row.execution
        if role == self.TransportRole:
            return row.transport
        if role == self.DriverRole:
            return row.driver
        if role == self.StageRole:
            return row.stage
        if role == self.ScheduleRole:
            return row.schedule
        if role == self.ClockRole:
            return row.clock
        if role == self.IntervalMsRole:
            return row.interval_ms
        if role == self.DelayMsRole:
            return row.delay_ms
        if role == self.PidRole:
            return row.pid
        if role == self.ParentRole:
            return row.parent
        if role == self.DepthRole:
            return row.depth
        if role == self.HasChildrenRole:
            return row.has_children
        if role == self.ExpandedRole:
            return row.expanded
        return None

    def roleNames(self) -> dict[int, QByteArray]:
        return {
            self.IdRole: QByteArray(b"id"),
            self.DisplayIdRole: QByteArray(b"displayId"),
            self.RoleRole: QByteArray(b"role"),
            self.KindRole: QByteArray(b"kind"),
            self.OwnerRole: QByteArray(b"owner"),
            self.StateRole: QByteArray(b"state"),
            self.ActivationRole: QByteArray(b"activation"),
            self.ExecutionRole: QByteArray(b"execution"),
            self.TransportRole: QByteArray(b"transport"),
            self.DriverRole: QByteArray(b"driver"),
            self.StageRole: QByteArray(b"stage"),
            self.ScheduleRole: QByteArray(b"schedule"),
            self.ClockRole: QByteArray(b"clock"),
            self.IntervalMsRole: QByteArray(b"intervalMs"),
            self.DelayMsRole: QByteArray(b"delayMs"),
            self.PidRole: QByteArray(b"pid"),
            self.ParentRole: QByteArray(b"parent"),
            self.DepthRole: QByteArray(b"depth"),
            self.HasChildrenRole: QByteArray(b"hasChildren"),
            self.ExpandedRole: QByteArray(b"expanded"),
        }

    def replace_rows(self, rows: list[_RuntimeRow]) -> None:
        self.beginResetModel()
        self._rows = list(rows)
        self.endResetModel()


@QmlElement
@QmlSingleton
class RuntimeViewModel(QObject):
    """Expose runtime units and scheduled tasks to QML."""

    REFRESH_INTERVAL_MS = 400
    FILTER_STATES = (
        "running",
        "idle",
        "declared",
        "completed",
        "failed",
        "stopped",
        "starting",
        "stopping",
        "incomplete",
    )

    unitsChanged = Signal()
    tasksChanged = Signal()
    summaryChanged = Signal()
    filtersChanged = Signal()
    sortChanged = Signal()

    def __init__(self, core: CoreRuntime, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._core = core
        self._units: list[dict[str, object]] = []
        self._tasks: list[str] = []
        self._summary = ""
        self._collapsed_unit_ids: set[str] = set()
        self._active_state_filters: set[str] = {"running", "idle", "declared", "completed", "failed"}
        self._sort_key = "id"
        self._sort_descending = False
        self._rows_model = _RuntimeRowsModel(self)
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
        raw_units: list[dict[str, object]] = [
            {
                "id": unit.id,
                "role": self._display_role(unit.role),
                "kind": self._display_kind(unit.kind, unit.role),
                "owner": unit.owner,
                "state": unit.state,
                "activation": self._display_activation(unit.activation_policy, unit.role),
                "execution": self._display_execution(unit.execution_policy, unit.role),
                "transport": unit.transport,
                "driver": unit.schedule_driver or "",
                "stage": unit.schedule_stage or "",
                "schedule": unit.schedule_kind,
                "clock": unit.schedule_clock,
                "intervalMs": "" if unit.interval_ms is None else str(unit.interval_ms),
                "delayMs": "" if unit.delay_ms is None else str(unit.delay_ms),
                "pid": self._display_pid(unit.pid, unit.role),
                "parent": self._display_parent(unit.parent_id or ""),
            }
            for unit in self._core.unit_infos()
        ]
        units = self._group_units(raw_units)
        tasks = list(self._core.scheduled_task_ids())
        counts = Counter(unit["state"] for unit in raw_units)
        summary = (
            f"units={len(raw_units)}  "
            f"running={counts.get('running', 0)}  "
            f"idle={counts.get('idle', 0)}  "
            f"stopped={counts.get('stopped', 0)}  "
            f"failed={counts.get('failed', 0)}  "
            f"tasks={len(tasks)}"
        )
        if len(units) != len(raw_units):
            summary += f"  shown={len(units)}"

        if units != self._units:
            self._units = units
            self._rows_model.replace_rows(self._build_rows(units))
            self.unitsChanged.emit()
        if tasks != self._tasks:
            self._tasks = tasks
            self.tasksChanged.emit()
        if summary != self._summary:
            self._summary = summary
            self.summaryChanged.emit()

    def _group_units(self, units: list[dict[str, object]]) -> list[dict[str, object]]:
        unit_by_id = {str(unit["id"]): unit for unit in units}
        by_parent: dict[str, list[dict[str, object]]] = {}
        roots: list[dict[str, object]] = []
        unit_ids = {str(unit["id"]) for unit in units}
        for unit in units:
            parent_id = str(unit["parent"])
            if not parent_id or parent_id not in unit_ids:
                roots.append(unit)
                continue
            by_parent.setdefault(parent_id, []).append(unit)

        visible_ids = self._visible_unit_ids(unit_by_id)
        grouped: list[dict[str, object]] = []
        seen: set[str] = set()

        def visit(unit: dict[str, object], depth: int) -> None:
            unit_id = str(unit["id"])
            if unit_id not in visible_ids:
                return
            if unit_id in seen:
                return
            seen.add(unit_id)
            child_units = [
                child for child in by_parent.get(unit_id, []) if str(child["id"]) in visible_ids
            ]
            child_units = self._sorted_units(child_units)
            has_children = len(child_units) > 0
            row = dict(unit)
            row["depth"] = depth
            row["displayId"] = self._display_unit_id(unit_id)
            row["hasChildren"] = has_children
            row["expanded"] = has_children and unit_id not in self._collapsed_unit_ids
            grouped.append(row)
            if unit_id in self._collapsed_unit_ids:
                return
            for child in child_units:
                visit(child, depth + 1)

        for root in self._sorted_units(roots):
            visit(root, 0)
        return grouped

    def _visible_unit_ids(
        self, unit_by_id: dict[str, dict[str, object]]
    ) -> set[str]:
        if not self._active_state_filters:
            return set(unit_by_id)
        visible_ids: set[str] = set()
        for unit_id, unit in unit_by_id.items():
            if str(unit["state"]) not in self._active_state_filters:
                continue
            current_id = unit_id
            while current_id:
                if current_id in visible_ids:
                    break
                visible_ids.add(current_id)
                parent_id = str(unit_by_id[current_id]["parent"])
                if not parent_id or parent_id not in unit_by_id:
                    break
                current_id = parent_id
        return visible_ids

    def _sorted_units(self, units: list[dict[str, object]]) -> list[dict[str, object]]:
        sort_key = self._sort_key

        def key_for(unit: dict[str, object]) -> tuple[int, object]:
            value = unit.get(sort_key, "")
            if sort_key == "pid":
                if not value:
                    return (1, 0)
                try:
                    return (0, int(str(value)))
                except ValueError:
                    return (0, str(value).lower())
            return (0, str(value).lower())

        return sorted(units, key=key_for, reverse=self._sort_descending)

    def _build_rows(self, units: list[dict[str, object]]) -> list[_RuntimeRow]:
        rows: list[_RuntimeRow] = []
        for unit in units:
            depth_value = unit["depth"]
            depth = depth_value if isinstance(depth_value, int) else 0
            rows.append(
                _RuntimeRow(
                    id=str(unit["id"]),
                    display_id=str(unit["displayId"]),
                    role=str(unit["role"]),
                    kind=str(unit["kind"]),
                    owner=str(unit["owner"]),
                    state=str(unit["state"]),
                    activation=str(unit["activation"]),
                    execution=str(unit["execution"]),
                    transport=str(unit["transport"]),
                    driver=str(unit["driver"]),
                    stage=str(unit["stage"]),
                    schedule=str(unit["schedule"]),
                    clock=str(unit["clock"]),
                    interval_ms=str(unit["intervalMs"]),
                    delay_ms=str(unit["delayMs"]),
                    pid=str(unit["pid"]),
                    parent=str(unit["parent"]),
                    depth=depth,
                    has_children=bool(unit["hasChildren"]),
                    expanded=bool(unit["expanded"]),
                )
            )
        return rows

    def _display_unit_id(self, unit_id: str) -> str:
        if unit_id.startswith("provider.export:"):
            _, provider_name, export_name = unit_id.split(":", 2)
            return f"provider.export:{provider_name}:{export_name}"
        return unit_id

    def _display_parent(self, parent_id: str) -> str:
        return self._display_unit_id(parent_id) if parent_id else ""

    def _display_role(self, role: str) -> str:
        if role == "provider.export":
            return "provider.surface"
        return role

    def _display_kind(self, kind: str, role: str) -> str:
        if role == "provider.export":
            return "export"
        return kind

    def _display_execution(self, execution: str, role: str) -> str:
        if role == "provider.export":
            return "surface"
        return execution

    def _display_activation(self, activation: str, role: str) -> str:
        if role == "provider.export":
            return "inherits"
        return activation

    def _display_pid(self, pid: int | None, role: str) -> str:
        if role == "provider.export" or pid is None:
            return ""
        return str(pid)

    @Slot()
    def copyOverview(self) -> None:
        clipboard = QGuiApplication.clipboard()
        if clipboard is None:
            return
        clipboard.setText(self._render_overview())

    @Slot(str)
    def toggleExpanded(self, unit_id: str) -> None:
        if not unit_id:
            return
        current_units = {str(unit["id"]): unit for unit in self._units}
        unit = current_units.get(unit_id)
        if unit is None or not bool(unit.get("hasChildren", False)):
            return
        if unit_id in self._collapsed_unit_ids:
            self._collapsed_unit_ids.remove(unit_id)
        else:
            self._collapsed_unit_ids.add(unit_id)
        self._refresh()

    @Slot(str)
    def toggleStateFilter(self, state: str) -> None:
        if state not in self.FILTER_STATES:
            return
        if state in self._active_state_filters:
            if len(self._active_state_filters) == 1:
                return
            self._active_state_filters.remove(state)
        else:
            self._active_state_filters.add(state)
        self.filtersChanged.emit()
        self._refresh()

    @Slot()
    def resetStateFilters(self) -> None:
        default_filters = {"running", "idle", "declared", "completed", "failed"}
        if self._active_state_filters == default_filters:
            return
        self._active_state_filters = set(default_filters)
        self.filtersChanged.emit()
        self._refresh()

    @Slot(str)
    def setSort(self, key: str) -> None:
        if key not in {"id", "state", "kind", "execution", "activation", "pid", "parent"}:
            return
        if self._sort_key == key:
            self._sort_descending = not self._sort_descending
        else:
            self._sort_key = key
            self._sort_descending = False
        self.sortChanged.emit()
        self._refresh()

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
            depth_value = unit["depth"]
            depth = depth_value if isinstance(depth_value, int) else 0
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
            if unit["stage"]:
                details.append(f"stage={unit['stage']}")
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
            lines.append(f"{'  ' * depth}{unit['id']} :: " + "  ".join(details))
        return "\n".join(lines)

    @Property(list, notify=unitsChanged)
    def units(self) -> list[dict[str, object]]:
        return self._units

    @Property(QObject, constant=True)
    def rowsModel(self) -> QObject:
        return self._rows_model

    @Property(list, notify=filtersChanged)
    def availableStateFilters(self) -> list[str]:
        return list(self.FILTER_STATES)

    @Property(list, notify=filtersChanged)
    def stateFilters(self) -> list[str]:
        return [state for state in self.FILTER_STATES if state in self._active_state_filters]

    @Property(str, notify=sortChanged)
    def sortKey(self) -> str:
        return self._sort_key

    @Property(bool, notify=sortChanged)
    def sortDescending(self) -> bool:
        return self._sort_descending

    @Property(list, notify=tasksChanged)
    def taskIds(self) -> list[str]:
        return self._tasks

    @Property(str, notify=summaryChanged)
    def summary(self) -> str:
        return self._summary
