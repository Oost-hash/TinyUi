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

#  TinyUI
"""Thin Qt adapter over the runtime inspector."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

from PySide6.QtCore import (
    Property,
    QAbstractListModel,
    QByteArray,
    QModelIndex,
    QObject,
    QPersistentModelIndex,
    QStandardPaths,
    Qt,
    QTimer,
    Signal,
    Slot,
)
from PySide6.QtGui import QGuiApplication

from tinycore.diagnostics.runtime_state import RuntimeInspector

_SKIP_PROPS = frozenset({"objectName"})


@dataclass(frozen=True)
class _QObjectSource:
    id: str
    label: str
    obj: QObject


@dataclass(frozen=True)
class _StateRow:
    row_type: str
    section_name: str
    section_title: str
    section_count: int
    collapsed: bool
    key: str
    value: str
    changed_at: int
    identity: tuple[str, str]


class _StateRowsModel(QAbstractListModel):
    RowTypeRole = int(Qt.ItemDataRole.UserRole) + 1
    SectionNameRole = int(Qt.ItemDataRole.UserRole) + 2
    SectionTitleRole = int(Qt.ItemDataRole.UserRole) + 3
    SectionCountRole = int(Qt.ItemDataRole.UserRole) + 4
    CollapsedRole = int(Qt.ItemDataRole.UserRole) + 5
    KeyRole = int(Qt.ItemDataRole.UserRole) + 6
    ValueRole = int(Qt.ItemDataRole.UserRole) + 7
    ChangedAtRole = int(Qt.ItemDataRole.UserRole) + 8

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._rows: list[_StateRow] = []

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
        if role == self.RowTypeRole:
            return row.row_type
        if role == self.SectionNameRole:
            return row.section_name
        if role == self.SectionTitleRole:
            return row.section_title
        if role == self.SectionCountRole:
            return row.section_count
        if role == self.CollapsedRole:
            return row.collapsed
        if role == self.KeyRole:
            return row.key
        if role == self.ValueRole:
            return row.value
        if role == self.ChangedAtRole:
            return row.changed_at
        return None

    def roleNames(self) -> dict[int, QByteArray]:
        return {
            self.RowTypeRole: QByteArray(b"rowType"),
            self.SectionNameRole: QByteArray(b"sectionName"),
            self.SectionTitleRole: QByteArray(b"sectionTitle"),
            self.SectionCountRole: QByteArray(b"sectionCount"),
            self.CollapsedRole: QByteArray(b"collapsed"),
            self.KeyRole: QByteArray(b"keyText"),
            self.ValueRole: QByteArray(b"valueText"),
            self.ChangedAtRole: QByteArray(b"changedAt"),
        }

    def replace_rows(self, rows: list[_StateRow]) -> None:
        old_identities = [row.identity for row in self._rows]
        new_identities = [row.identity for row in rows]
        if old_identities != new_identities:
            self.beginResetModel()
            self._rows = list(rows)
            self.endResetModel()
            return

        if not rows:
            return

        changed_indexes: list[int] = []
        for index, (old, new) in enumerate(zip(self._rows, rows)):
            if old != new:
                self._rows[index] = new
                changed_indexes.append(index)

        for index in changed_indexes:
            model_index = self.index(index, 0)
            self.dataChanged.emit(
                model_index,
                model_index,
                [
                    self.SectionCountRole,
                    self.CollapsedRole,
                    self.KeyRole,
                    self.ValueRole,
                    self.ChangedAtRole,
                ],
            )


class StateMonitorViewModel(QObject):
    """Expose runtime inspector state to QML."""

    _REFRESH_INTERVAL_MS = 200
    _CAPTURE_FLUSH_INTERVAL_MS = 1000

    sourcesChanged = Signal()
    selectedChanged = Signal()
    entriesChanged = Signal()
    sectionsChanged = Signal()
    captureChanged = Signal()

    def __init__(self, inspector: RuntimeInspector, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._inspector = inspector
        self._qobject_sources: list[_QObjectSource] = []
        self._selected_index = -1
        self._entries: list[dict[str, object]] = []
        self._rows_model = _StateRowsModel(self)
        self._collapsed_by_source: dict[str, set[str]] = {}
        self._timer = QTimer(self)
        self._timer.setInterval(self._REFRESH_INTERVAL_MS)
        self._timer.timeout.connect(self._refresh)
        self._capture_source_id: str | None = None
        self._capture_path: Path | None = None
        self._capture_queue: list[dict[str, object]] = []
        self._capture_flush_timer = QTimer(self)
        self._capture_flush_timer.setInterval(self._CAPTURE_FLUSH_INTERVAL_MS)
        self._capture_flush_timer.timeout.connect(self._flush_capture_queue)

        if self._inspector.sources():
            self._selected_index = 0

    @property
    def refresh_interval_ms(self) -> int:
        return self._REFRESH_INTERVAL_MS

    @property
    def capture_flush_interval_ms(self) -> int:
        return self._CAPTURE_FLUSH_INTERVAL_MS

    def register_object(self, label: str, obj: QObject) -> None:
        """Register a QObject source locally in the Qt adapter layer."""
        self._qobject_sources.append(_QObjectSource(f"qobject:{label}", label, obj))
        if self._selected_index < 0 and self._all_sources():
            self._selected_index = 0
            self.selectedChanged.emit()
        self.sourcesChanged.emit()

    def start(self) -> None:
        """Start refreshing inspector snapshots."""
        self._timer.start()

    def shutdown(self) -> None:
        self._timer.stop()
        self._flush_capture_queue()
        self._capture_flush_timer.stop()

    def _refresh(self) -> None:
        if self._selected_index < 0:
            return

        sources = self._all_sources()
        if self._selected_index >= len(sources):
            return

        selected = sources[self._selected_index]
        if selected["kind"] == "qobject":
            snapshot = self._snapshot_qobject(selected["id"])
        else:
            snapshot = self._inspector.snapshot(selected["id"])
        entries: list[dict[str, object]] = []
        for entry in snapshot:
            if isinstance(entry, dict):
                entries.append(entry)
            else:
                entries.append(
                    {
                        "key": entry.key,
                        "value": entry.value,
                        "changed": entry.changed,
                        "changedAt": entry.changed_at,
                    }
                )
        self._entries = entries
        self._rows_model.replace_rows(self._build_rows(selected["id"], entries))
        self._queue_capture(selected["id"], selected["label"], entries)
        self.entriesChanged.emit()

    def _all_sources(self) -> list[dict[str, str]]:
        runtime_sources = [
            {"id": info.id, "label": info.label, "kind": info.kind}
            for info in self._inspector.sources()
        ]
        qobject_sources = [
            {"id": source.id, "label": source.label, "kind": "qobject"}
            for source in self._qobject_sources
        ]
        return runtime_sources + qobject_sources

    def _snapshot_qobject(self, source_id: str) -> list[dict[str, object]]:
        source = next((item for item in self._qobject_sources if item.id == source_id), None)
        if source is None:
            return []

        entries = []
        meta = source.obj.metaObject()
        for index in range(meta.propertyCount()):
            prop = meta.property(index)
            name = prop.name()
            if name in _SKIP_PROPS:
                continue
            try:
                value = prop.read(source.obj)
                if isinstance(value, list):
                    rendered = f"[{len(value)} items]"
                elif isinstance(value, dict):
                    rendered = "{…}"
                else:
                    try:
                        rendered = f"{float(value):.6g}"
                    except (ValueError, TypeError):
                        rendered = str(value)
            except Exception as exc:
                rendered = f"err: {exc}"
            entries.append(
                {
                    "key": name,
                    "value": rendered,
                    "changed": False,
                    "changedAt": 0,
                }
            )
        return entries

    def _build_rows(
        self, source_id: str, entries: list[dict[str, object]]
    ) -> list[_StateRow]:
        grouped: dict[str, list[dict[str, object]]] = {}
        order: list[str] = []
        for entry in entries:
            key = str(entry["key"])
            if "." in key:
                section, leaf = key.split(".", 1)
            else:
                section, leaf = "general", key
            if section not in grouped:
                grouped[section] = []
                order.append(section)
            grouped[section].append(
                {
                    "key": leaf,
                    "fullKey": key,
                    "value": entry["value"],
                    "changed": entry["changed"],
                    "changedAt": entry["changedAt"],
                }
            )

        collapsed = self._collapsed_by_source.setdefault(source_id, set())
        rows: list[_StateRow] = []
        for section in order:
            section_title = section.replace("_", " ").title()
            section_entries = grouped[section]
            is_collapsed = section in collapsed
            rows.append(
                _StateRow(
                    row_type="section",
                    section_name=section,
                    section_title=section_title,
                    section_count=len(section_entries),
                    collapsed=is_collapsed,
                    key="",
                    value="",
                    changed_at=0,
                    identity=("section", section),
                )
            )
            if is_collapsed:
                continue
            for entry in section_entries:
                changed_at = entry["changedAt"]
                rows.append(
                    _StateRow(
                        row_type="entry",
                        section_name=section,
                        section_title=section_title,
                        section_count=len(section_entries),
                        collapsed=False,
                        key=str(entry["key"]),
                        value=str(entry["value"]),
                        changed_at=int(changed_at) if isinstance(changed_at, int | float) else 0,
                        identity=("entry", str(entry["fullKey"])),
                    )
                )
        return rows

    @Property(list, notify=sourcesChanged)
    def sources(self) -> list[dict[str, object]]:
        return [
            {"label": info["label"], "index": index}
            for index, info in enumerate(self._all_sources())
        ]

    @Property(int, notify=selectedChanged)
    def selectedIndex(self) -> int:
        return self._selected_index

    @Property(bool, notify=selectedChanged)
    def hasSelectedSource(self) -> bool:
        return 0 <= self._selected_index < len(self._all_sources())

    @Slot(int)
    def selectSource(self, index: int) -> None:
        if 0 <= index < len(self._all_sources()) and index != self._selected_index:
            self._selected_index = index
            self._entries = []
            self._rows_model.replace_rows([])
            self.selectedChanged.emit()
            self.entriesChanged.emit()

    @Slot(str)
    def toggleSection(self, name: str) -> None:
        sources = self._all_sources()
        if not (0 <= self._selected_index < len(sources)):
            return
        source_id = sources[self._selected_index]["id"]
        collapsed = self._collapsed_by_source.setdefault(source_id, set())
        if name in collapsed:
            collapsed.remove(name)
        else:
            collapsed.add(name)
        self._rows_model.replace_rows(self._build_rows(source_id, self._entries))

    @Slot(str, str)
    def copyEntry(self, key: str, value: str) -> None:
        clipboard = QGuiApplication.clipboard()
        if clipboard is None:
            return
        clipboard.setText(f"{key}: {value}")

    @Slot()
    def copyAllEntries(self) -> None:
        clipboard = QGuiApplication.clipboard()
        if clipboard is None:
            return
        if not self._entries:
            clipboard.setText("")
            return
        lines = [f"{entry['key']}: {entry['value']}" for entry in self._entries]
        clipboard.setText("\n".join(lines))

    @Slot()
    def toggleCapture(self) -> None:
        if self._capture_source_id is not None:
            self._flush_capture_queue()
            self._capture_flush_timer.stop()
            self._capture_source_id = None
            self._capture_path = None
            self.captureChanged.emit()
            return

        sources = self._all_sources()
        if not (0 <= self._selected_index < len(sources)):
            return

        selected = sources[self._selected_index]
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        safe_label = "".join(
            char.lower() if char.isalnum() else "-"
            for char in selected["label"]
        ).strip("-")
        filename = f"{stamp}-{safe_label or 'source'}.jsonl"
        capture_dir = self._capture_dir()
        capture_dir.mkdir(parents=True, exist_ok=True)
        self._capture_source_id = selected["id"]
        self._capture_path = capture_dir / filename
        self._capture_queue.clear()
        self._capture_flush_timer.start()
        self.captureChanged.emit()

    @Slot()
    def copyCapturePath(self) -> None:
        clipboard = QGuiApplication.clipboard()
        if clipboard is None or self._capture_path is None:
            return
        clipboard.setText(str(self._capture_path))

    def _capture_dir(self) -> Path:
        appdata_root = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.AppDataLocation
        )
        if appdata_root:
            return Path(appdata_root) / "TinyUi" / "devtools-captures"
        return Path.home() / ".tinyui" / "devtools-captures"

    def _queue_capture(
        self,
        source_id: str,
        source_label: str,
        entries: list[dict[str, object]],
    ) -> None:
        if self._capture_source_id != source_id or self._capture_path is None or not entries:
            return

        self._capture_queue.append(
            {
                "ts": datetime.now(timezone.utc).isoformat(),
                "source_id": source_id,
                "source_label": source_label,
                "entries": entries,
            }
        )

    def _flush_capture_queue(self) -> None:
        if self._capture_path is None or not self._capture_queue:
            return

        payloads = self._capture_queue
        self._capture_queue = []
        lines = [
            json.dumps(payload, ensure_ascii=True)
            for payload in payloads
        ]
        with self._capture_path.open("a", encoding="utf-8") as handle:
            handle.write("\n".join(lines))
            handle.write("\n")

    @Property(list, notify=entriesChanged)
    def entries(self) -> list[dict[str, object]]:
        return self._entries

    @Property(QObject, constant=True)
    def sectionModel(self) -> QObject:
        return self._rows_model

    @Property(bool, notify=captureChanged)
    def captureActive(self) -> bool:
        return self._capture_source_id is not None and self._capture_path is not None

    @Property(str, notify=captureChanged)
    def capturePath(self) -> str:
        return "" if self._capture_path is None else str(self._capture_path)
