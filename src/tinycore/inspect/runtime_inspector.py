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
"""Runtime-owned inspection service for Dev Tools and diagnostics."""

from __future__ import annotations

import inspect
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable

from tinycore.log import get_logger

if TYPE_CHECKING:
    from tinycore.session.runtime import SessionRuntime

_log = get_logger(__name__)
FieldReader = Callable[[str, str, object], object]
SnapshotFn = Callable[[], list[tuple[str, str]]]


def _render_value(value: object) -> str:
    if isinstance(value, int | float):
        return f"{float(value):.6g}"
    return str(value)


def _to_int(value: object) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        return int(value)
    raise TypeError(f"cannot render int from {type(value).__name__}")


def _to_float(value: object) -> float:
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, int | float):
        return float(value)
    if isinstance(value, str):
        return float(value)
    raise TypeError(f"cannot render float from {type(value).__name__}")


def _render_schema_value(value: object, render: str) -> str:
    if render == "str":
        return str(value)
    if render == "bool":
        return str(bool(value))
    if render == "int":
        return str(_to_int(value))
    if render == "float_1":
        return f"{_to_float(value):.1f}"
    if render == "float_2":
        return f"{_to_float(value):.2f}"
    if render == "float_3":
        return f"{_to_float(value):.3f}"
    if render == "kmh_1":
        return f"{_to_float(value) * 3.6:.1f} km/h"
    if render == "seconds_1":
        return f"{_to_float(value):.1f} s"
    if render == "seconds_3":
        return f"{_to_float(value):.3f} s"
    if render == "celsius_1":
        return f"{_to_float(value):.1f} C"
    if render == "percent_1":
        return f"{_to_float(value) * 100:.1f} %"
    if render == "join":
        if isinstance(value, tuple | list):
            return ", ".join(str(item) for item in value)
        return str(value)
    return _render_value(value)


def _resolve_path_value(root: object, path: str) -> object:
    value = root
    for part in path.split("."):
        value = getattr(value, part)
        if callable(value):
            signature = inspect.signature(value)
            parameters = tuple(signature.parameters.values())
            if all(
                parameter.kind in (
                    inspect.Parameter.VAR_POSITIONAL,
                    inspect.Parameter.VAR_KEYWORD,
                )
                or parameter.default is not inspect.Parameter.empty
                for parameter in parameters
            ):
                value = value()
    return value


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
            return _render_value(value)
        except Exception as exc:
            return f"err: {exc}"


class _ProviderTelemetrySource(_Source):
    def __init__(self, source_id: str, label: str, provider) -> None:
        self._provider = provider
        super().__init__(source_id, label, "provider", self._snapshot)

    def _snapshot(self) -> list[tuple[str, str]]:
        schema_fn = getattr(self._provider, "inspect_schema", None)
        if schema_fn is not None:
            try:
                schema = schema_fn()
                return self._schema_snapshot(schema)
            except Exception as exc:
                return [("provider.inspect_schema", f"err: {exc}")]
        snapshot = getattr(self._provider, "inspect_snapshot", None)
        if snapshot is None:
            return [("provider.inspect", "err: provider has no inspect_schema()")]
        try:
            return snapshot()
        except Exception as exc:
            return [("provider.inspect", f"err: {exc}")]

    def _schema_snapshot(self, schema) -> list[tuple[str, str]]:
        entries: list[tuple[str, str]] = []
        for field in schema:
            try:
                value = _resolve_path_value(self._provider, field.path)
                if field.key == "opponents.p1.driver":
                    value = self._provider.opponents.driver_name(0)
                elif field.key == "opponents.p1.place":
                    value = self._provider.opponents.place(0)
                elif field.key == "opponents.p1.in_pits":
                    value = self._provider.opponents.in_pits(0)
                elif field.key == "opponents.p1.gap_to_leader":
                    value = self._provider.opponents.gap_to_leader(0)
                elif field.key == "tyre.compound_f":
                    value = self._provider.tyre.compound_name()[0]
                elif field.key == "tyre.compound_r":
                    value = self._provider.tyre.compound_name()[1]
                entries.append((field.key, _render_schema_value(value, field.render)))
            except Exception as exc:
                entries.append((field.key, f"err: {exc}"))
        return entries


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
