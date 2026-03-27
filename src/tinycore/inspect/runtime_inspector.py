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
"""Runtime-owned inspection snapshots and change tracking."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable

SnapshotFn = Callable[[], list[tuple[str, str]]]
@dataclass(frozen=True)
class InspectionSourceInfo:
    """User-facing source metadata."""

    id: str
    label: str
    kind: str


@dataclass(frozen=True)
class InspectionEntry:
    """One runtime inspection entry."""

    key: str
    value: str
    changed: bool = False
    changed_at: int = 0


class _Source:
    def __init__(self, source_id: str, label: str, kind: str, snapshot_fn: SnapshotFn) -> None:
        self.id = source_id
        self.label = label
        self.kind = kind
        self._snapshot_fn = snapshot_fn

    def info(self) -> InspectionSourceInfo:
        return InspectionSourceInfo(id=self.id, label=self.label, kind=self.kind)

    def snapshot(self) -> list[tuple[str, str]]:
        return self._snapshot_fn()


class RuntimeInspector:
    """Generic runtime-owned inspection source registry and change tracker."""

    def __init__(self) -> None:
        self._sources: list[_Source] = []
        self._sources_by_id: dict[str, _Source] = {}
        self._prev_by_source: dict[str, dict[str, str]] = {}
        self._changed_at_by_source: dict[str, dict[str, int]] = {}

    def add_snapshot_source(
        self,
        source_id: str,
        label: str,
        kind: str,
        snapshot_fn: SnapshotFn,
    ) -> None:
        """Register one inspection source."""
        source = _Source(source_id, label, kind, snapshot_fn)
        self._sources.append(source)
        self._sources_by_id[source.id] = source

    def sources(self) -> list[InspectionSourceInfo]:
        """Return all available inspection sources."""
        return [source.info() for source in self._sources]

    def snapshot(self, source_id: str) -> list[InspectionEntry]:
        """Return a change-tracked snapshot for one source."""
        source = self._sources_by_id.get(source_id)
        if source is None:
            return []

        raw_entries = source.snapshot()
        previous = self._prev_by_source.setdefault(source_id, {})
        changed_at = self._changed_at_by_source.setdefault(source_id, {})
        now_ms = int(time.time() * 1000)
        entries: list[InspectionEntry] = []

        for key, value in raw_entries:
            changed = value != previous.get(key)
            if changed:
                previous[key] = value
                changed_at[key] = now_ms
            entries.append(
                InspectionEntry(
                    key=key,
                    value=value,
                    changed=changed,
                    changed_at=changed_at.get(key, 0),
                )
            )

        return entries
