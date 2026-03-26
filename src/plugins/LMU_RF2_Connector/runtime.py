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

"""Runtime entrypoint and source orchestration for the consolidated connector family."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, cast

from .contracts.inspect_schema import provider_inspection_schema
from .contracts.source import ConnectorSource
from .contracts.telemetry import TelemetryReader
from .sources.lmu import LMULiveSource
from .sources.mock import MockSource
from .sources.rf2 import RF2LiveSource


@dataclass(frozen=True)
class SourceDescriptor:
    name: str
    kind: str
    game: str
    description: str


class ConfigurableMockSource(Protocol):
    @property
    def min_val(self) -> float: ...
    @property
    def max_val(self) -> float: ...
    @property
    def step(self) -> float: ...
    def configure(self, minimum: float, maximum: float, step: float) -> None: ...


class ConnectorRuntime(TelemetryReader):
    """Host-facing connector runtime that owns source selection and telemetry exposure."""

    family_name = "LMU_RF2_Connector"

    def __init__(self, *sources: ConnectorSource) -> None:
        self._sources: dict[str, ConnectorSource] = {}
        self._active_source_name: str | None = None
        self._opened = False
        self._demo_owners: set[str] = set()
        self._source_requests: dict[str, str] = {}
        self._preferred_source_name: str | None = None
        self.register_source(MockSource())
        for source in sources:
            self.register_source(source)
        if sources:
            self._active_source_name = sources[0].name

    def register_source(self, source: ConnectorSource) -> None:
        self._sources[source.name] = source
        if self._active_source_name is None:
            self._active_source_name = source.name
        if self._preferred_source_name is None and source.kind != "mock":
            self._preferred_source_name = source.name

    def source_names(self) -> tuple[str, ...]:
        return tuple(self._sources.keys())

    def descriptors(self) -> tuple[SourceDescriptor, ...]:
        return tuple(
            SourceDescriptor(
                name=source.name,
                kind=source.kind,
                game=source.game,
                description=source.description,
            )
            for source in self._sources.values()
        )

    def source(self, name: str) -> ConnectorSource | None:
        return self._sources.get(name)

    def active_source_name(self) -> str | None:
        return self._active_source_name

    def active_source_handle(self) -> ConnectorSource | None:
        if self._active_source_name is None:
            return None
        return self._sources.get(self._active_source_name)

    def open(self) -> None:
        self._opened = True
        self._require_active_source().open()

    def close(self) -> None:
        active = self.active_source_handle()
        if active is not None:
            active.close()
        self._opened = False

    def update(self) -> None:
        self._require_active_source().update()

    def request_demo_mode(self, owner: str) -> None:
        self._demo_owners.add(owner)
        self._sync_active_source()

    def release_demo_mode(self, owner: str) -> None:
        self._demo_owners.discard(owner)
        self._sync_active_source()

    def supports_source(self, name: str) -> bool:
        return name in self._sources

    def request_source(self, owner: str, name: str) -> bool:
        if not self.supports_source(name):
            return False
        self._source_requests[owner] = name
        if name != "mock":
            self._preferred_source_name = name
        self._sync_active_source()
        return True

    def release_source(self, owner: str) -> bool:
        removed = self._source_requests.pop(owner, None)
        if removed is None:
            return False
        self._sync_active_source()
        return True

    def mode(self) -> str:
        active = self.active_source_handle()
        if active is None:
            return "inactive"
        return "demo" if active.kind == "mock" else "real"

    def active_game(self) -> str:
        active = self.active_source_handle()
        return active.game if active is not None else "none"

    def active_source(self) -> str:
        active = self.active_source_handle()
        return active.name if active is not None else "none"

    def supports_demo_mode(self) -> bool:
        return "mock" in self._sources

    def demo_owner_count(self) -> int:
        return len(self._demo_owners)

    def source_request_count(self) -> int:
        return len(self._source_requests)

    def demo_min(self) -> float:
        return self._mock_source().min_val if self.supports_demo_mode() else 0.0

    def demo_max(self) -> float:
        return self._mock_source().max_val if self.supports_demo_mode() else 0.0

    def demo_speed(self) -> float:
        return self._mock_source().step if self.supports_demo_mode() else 0.0

    def set_demo_min(self, value: float) -> None:
        mock = self._mock_source()
        mock.configure(value, mock.max_val, mock.step)

    def set_demo_max(self, value: float) -> None:
        mock = self._mock_source()
        mock.configure(mock.min_val, value, mock.step)

    def set_demo_speed(self, value: float) -> None:
        mock = self._mock_source()
        mock.configure(mock.min_val, mock.max_val, value)

    def inspect_schema(self):
        return provider_inspection_schema()

    def raw_snapshot(self) -> list[tuple[str, str]]:
        active = self.active_source_handle()
        if active is None:
            return [("meta.status", "inactive")]
        snapshot: list[tuple[str, str]] = [
            ("meta.family", self.family_name),
            ("meta.source", active.name),
            ("meta.game", active.game),
            ("meta.kind", active.kind),
        ]
        raw_snapshot_fn = getattr(active.reader, "raw_snapshot", None)
        if not callable(raw_snapshot_fn):
            snapshot.append(("meta.raw", "not supported"))
            return snapshot
        try:
            raw_entries = cast(list[tuple[str, str]], raw_snapshot_fn())
            snapshot.extend(raw_entries)
        except Exception as exc:
            snapshot.append(("meta.raw", f"err: {exc}"))
        return snapshot

    @property
    def state(self): return self._reader.state
    @property
    def brake(self): return self._reader.brake
    @property
    def electric_motor(self): return self._reader.electric_motor
    @property
    def engine(self): return self._reader.engine
    @property
    def inputs(self): return self._reader.inputs
    @property
    def lap(self): return self._reader.lap
    @property
    def session(self): return self._reader.session
    @property
    def track(self): return self._reader.track
    @property
    def opponents(self): return self._reader.opponents
    @property
    def switch(self): return self._reader.switch
    @property
    def timing(self): return self._reader.timing
    @property
    def tyre(self): return self._reader.tyre
    @property
    def vehicle(self): return self._reader.vehicle
    @property
    def wheel(self): return self._reader.wheel

    @property
    def _reader(self) -> TelemetryReader:
        return self._require_active_source().reader

    def _switch_source(self, name: str) -> None:
        previous = self.active_source_handle()
        if previous is not None and previous.name == name:
            return
        was_open = self._opened
        if previous is not None and was_open:
            previous.close()
        self._active_source_name = name
        next_source = self._require_active_source()
        if next_source.kind != "mock":
            self._preferred_source_name = next_source.name
        if was_open:
            next_source.open()

    def _sync_active_source(self) -> None:
        target_name = self._requested_source_name()
        if target_name is not None:
            self._switch_source(target_name)

    def _require_active_source(self) -> ConnectorSource:
        active = self.active_source_handle()
        if active is None:
            raise RuntimeError("No active connector source has been registered")
        return active

    def _first_non_mock_source_name(self) -> str | None:
        for source in self._sources.values():
            if source.kind != "mock":
                return source.name
        return None

    def _requested_source_name(self) -> str | None:
        if self._demo_owners and self.supports_source("mock"):
            return "mock"
        if self._source_requests:
            return next(reversed(self._source_requests.values()))
        return self._preferred_source_name or self._first_non_mock_source_name()

    def _mock_source(self) -> ConfigurableMockSource:
        source = self.source("mock")
        if source is None:
            raise RuntimeError("Mock source is not registered")
        return cast(ConfigurableMockSource, source)


def create_provider(*sources: ConnectorSource) -> ConnectorRuntime:
    return ConnectorRuntime(*sources)


def create_lmu_provider() -> ConnectorRuntime:
    return create_provider(LMULiveSource())


def create_lmu_rf2_provider() -> ConnectorRuntime:
    return create_provider(LMULiveSource(), RF2LiveSource())
