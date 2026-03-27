"""Shared inspection protocols for plugin- and provider-owned diagnostics."""

from __future__ import annotations

from typing import Protocol, TypeAlias


InspectionSnapshot: TypeAlias = list[tuple[str, str]]


class InspectionSnapshotProvider(Protocol):
    """Minimal protocol for objects that expose devtools inspection snapshots."""

    def inspect_snapshot(self) -> InspectionSnapshot: ...
