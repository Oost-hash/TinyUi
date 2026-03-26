#  TinyUI
"""Runtime-owned inspection service for Dev Tools and diagnostics."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable

from tinycore.log import get_logger

if TYPE_CHECKING:
    from tinycore.session.runtime import SessionRuntime

_log = get_logger(__name__)
FieldReader = Callable[[str, str, object], object]
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


class _FieldSource(_Source):
    def __init__(
        self,
        source_id: str,
        label: str,
        capability: str,
        provider,
        fields: list[str],
        field_reader: FieldReader,
    ) -> None:
        self._capability = capability
        self._provider = provider
        self._fields = fields
        self._field_reader = field_reader
        super().__init__(source_id, label, "field", self._snapshot)

    def _snapshot(self) -> list[tuple[str, str]]:
        return [(field, self._read(field)) for field in self._fields]

    def _read(self, field: str) -> str:
        try:
            value = self._field_reader(self._capability, field, self._provider)
            try:
                return f"{float(value):.6g}"
            except (ValueError, TypeError):
                return str(value)
        except Exception as exc:
            return f"err: {exc}"


class _ProviderTelemetrySource(_Source):
    def __init__(self, source_id: str, label: str, provider) -> None:
        self._provider = provider
        super().__init__(source_id, label, "provider", self._snapshot)

    def _snapshot(self) -> list[tuple[str, str]]:
        snapshot = getattr(self._provider, "inspect_snapshot", None)
        if snapshot is None:
            return [("provider.inspect", "err: provider has no inspect_snapshot()")]
        try:
            return snapshot()
        except Exception as exc:
            return [("provider.inspect", f"err: {exc}")]


class RuntimeInspector:
    """Runtime-owned inspection service used by Dev Tools and diagnostics."""

    def __init__(self) -> None:
        self._sources: list[_Source] = []
        self._sources_by_id: dict[str, _Source] = {}
        self._prev_by_source: dict[str, dict[str, str]] = {}
        self._changed_at_by_source: dict[str, dict[str, int]] = {}

    def setup(
        self,
        session: "SessionRuntime",
        widget_sources: list[tuple[str, str, str]],
        field_reader: FieldReader,
    ) -> None:
        """Register runtime-backed inspection sources."""
        by_consumer: dict[str, dict[str, list[str]]] = {}
        for consumer_name, capability, field in widget_sources:
            by_consumer.setdefault(consumer_name, {}).setdefault(capability, []).append(field)

        for consumer_name, fields_by_capability in by_consumer.items():
            seen_provider_names: set[str] = set()
            for capability, fields in fields_by_capability.items():
                binding = session.bindings_for(consumer_name).get(capability)
                if binding is None:
                    continue

                if binding.provider_name not in seen_provider_names:
                    handle = session.provider(binding.provider_name)
                    if handle is not None:
                        self.add_source(
                            _ProviderTelemetrySource(
                                f"provider:{binding.provider_name}:telemetry",
                                f"State: {binding.provider_name}",
                                handle.provider,
                            )
                        )
                        seen_provider_names.add(binding.provider_name)

                self.add_source(
                    _FieldSource(
                        f"field:{consumer_name}:{capability}",
                        f"Polling: {consumer_name} [{capability}]",
                        capability,
                        binding.provider,
                        fields,
                        field_reader,
                    )
                )

        _log.info("runtime inspector setup: %d sources", len(self._sources))

    def add_source(self, source: _Source) -> None:
        """Register one inspection source."""
        self._sources.append(source)
        self._sources_by_id[source.id] = source

    def add_snapshot_source(
        self,
        source_id: str,
        label: str,
        kind: str,
        snapshot_fn: SnapshotFn,
    ) -> None:
        """Register a generic snapshot source."""
        self.add_source(_Source(source_id, label, kind, snapshot_fn))

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
