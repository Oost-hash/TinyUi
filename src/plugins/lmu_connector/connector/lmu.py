#  TinyUI
"""LMU provider-family runtime."""

from __future__ import annotations

from time import monotonic

from tinycore.log import get_logger

from .inspect import provider_inspection_snapshot, reader_inspection_snapshot
from .mock import LMUMockConnector
from .reader import ElectricMotor, TelemetryReader
from .session import LMULapProvider, LMUSessionProvider, LMUStateProvider, LMUTimingProvider
from .source import LMUSource
from .tyre import LMUTyreProvider
from .vehicle import (
    LMUBrakeProvider,
    LMUEngineProvider,
    LMUInputsProvider,
    LMUSwitchProvider,
    LMUVehicleProvider,
    LMUWheelProvider,
)

_log = get_logger(__name__)
_DEMO_GRACE_SECONDS = 30.0


class LMUElectricMotorProvider(ElectricMotor):
    """LMU has no hybrid data — returns neutral/zero values."""

    def state(self, index: int | None = None) -> int:
        return 0

    def battery_charge(self, index: int | None = None) -> float:
        return 0.0

    def rpm(self, index: int | None = None) -> float:
        return 0.0

    def torque(self, index: int | None = None) -> float:
        return 0.0

    def motor_temperature(self, index: int | None = None) -> float:
        return 0.0

    def water_temperature(self, index: int | None = None) -> float:
        return 0.0


class LMURealConnector(TelemetryReader):
    """Thin composition layer over the LMU shared-memory source."""

    def __init__(self) -> None:
        self._source = LMUSource()
        self._state = LMUStateProvider(self._source)
        self._brake = LMUBrakeProvider(self._source)
        self._electric_motor = LMUElectricMotorProvider()
        self._engine = LMUEngineProvider(self._source)
        self._inputs = LMUInputsProvider(self._source)
        self._lap = LMULapProvider(self._source)
        self._session = LMUSessionProvider(self._source)
        self._switch = LMUSwitchProvider(self._source)
        self._timing = LMUTimingProvider(self._source)
        self._tyre = LMUTyreProvider(self._source)
        self._vehicle = LMUVehicleProvider(self._source)
        self._wheel = LMUWheelProvider(self._source)

    @property
    def source(self) -> LMUSource:
        return self._source

    def open(self) -> None:
        self._source.open()

    def close(self) -> None:
        self._source.close()

    def update(self) -> None:
        self._source.update()

    @property
    def state(self):
        return self._state

    @property
    def brake(self):
        return self._brake

    @property
    def electric_motor(self):
        return self._electric_motor

    @property
    def engine(self):
        return self._engine

    @property
    def inputs(self):
        return self._inputs

    @property
    def lap(self):
        return self._lap

    @property
    def session(self):
        return self._session

    @property
    def switch(self):
        return self._switch

    @property
    def timing(self):
        return self._timing

    @property
    def tyre(self):
        return self._tyre

    @property
    def vehicle(self):
        return self._vehicle

    @property
    def wheel(self):
        return self._wheel

    def inspect_snapshot(self) -> list[tuple[str, str]]:
        return reader_inspection_snapshot(self)


class LMUConnector(TelemetryReader):
    """Provider runtime that owns both real and demo LMU sources."""

    def __init__(self) -> None:
        self._real = LMURealConnector()
        self._mock = LMUMockConnector()
        self._real_open = False
        self._mock_open = False
        self._demo_owners: set[str] = set()
        self._demo_grace_until: float | None = None

    def open(self) -> None:
        if not self._real_open:
            self._real.open()
            self._real_open = True

    def close(self) -> None:
        if self._mock_open:
            self._mock.close()
            self._mock_open = False
        if self._real_open:
            self._real.close()
            self._real_open = False

    def update(self) -> None:
        if self._real_open:
            try:
                self._real.update()
            except Exception as exc:
                _log.warning("LMU real source update failed: %s", exc)

        if self._demo_enabled():
            self._ensure_mock_open()
            self._mock.update()
            return

        if self._mock_open:
            self._mock.close()
            self._mock_open = False
            _log.info("LMU demo mode stopped")

    def request_demo_mode(self, owner: str) -> None:
        first_owner = not self._demo_owners
        self._demo_owners.add(owner)
        self._demo_grace_until = None
        if first_owner:
            _log.info("LMU demo mode requested  owner=%s", owner)

    def release_demo_mode(self, owner: str) -> None:
        self._demo_owners.discard(owner)
        if self._demo_owners:
            return
        self._demo_grace_until = monotonic() + _DEMO_GRACE_SECONDS
        _log.info("LMU demo mode grace started  owner=%s  seconds=%s", owner, _DEMO_GRACE_SECONDS)

    def mode(self) -> str:
        if self._demo_enabled():
            return "demo"
        if self._real_active():
            return "real"
        return "inactive"

    def active_game(self) -> str:
        if self._demo_enabled():
            return "mock"
        if self._real_active():
            return "lmu"
        return "none"

    def supports_demo_mode(self) -> bool:
        return True

    def demo_min(self) -> float:
        return self._mock.min_val

    def demo_max(self) -> float:
        return self._mock.max_val

    def demo_speed(self) -> float:
        return self._mock.step

    def set_demo_min(self, value: float) -> None:
        self._mock.configure(value, self._mock.max_val, self._mock.step)

    def set_demo_max(self, value: float) -> None:
        self._mock.configure(self._mock.min_val, value, self._mock.step)

    def set_demo_speed(self, value: float) -> None:
        self._mock.configure(self._mock.min_val, self._mock.max_val, value)

    def inspect_snapshot(self) -> list[tuple[str, str]]:
        mode = self.mode()
        active_reader = None if mode == "inactive" else self._active_reader
        return provider_inspection_snapshot(
            mode=mode,
            active_game=self.active_game(),
            supports_demo=self.supports_demo_mode(),
            demo_enabled=self._demo_enabled(),
            demo_owner_count=len(self._demo_owners),
            demo_grace_active=self._demo_grace_until is not None,
            demo_min=self.demo_min(),
            demo_max=self.demo_max(),
            demo_speed=self.demo_speed(),
            real_open=self._real_open,
            mock_open=self._mock_open,
            active_reader=active_reader,
        )

    @property
    def real(self) -> LMURealConnector:
        return self._real

    def _demo_enabled(self) -> bool:
        if self._demo_owners:
            return True
        return bool(self._demo_grace_until and monotonic() < self._demo_grace_until)

    def _ensure_mock_open(self) -> None:
        if self._mock_open:
            return
        self._mock.open()
        self._mock_open = True
        _log.info("LMU demo mode started")

    def _real_active(self) -> bool:
        try:
            return self._real.state.active()
        except Exception:
            return False

    @property
    def _active_reader(self) -> TelemetryReader:
        return self._mock if self._demo_enabled() else self._real

    @property
    def state(self):
        return self._active_reader.state

    @property
    def brake(self):
        return self._active_reader.brake

    @property
    def electric_motor(self):
        return self._active_reader.electric_motor

    @property
    def engine(self):
        return self._active_reader.engine

    @property
    def inputs(self):
        return self._active_reader.inputs

    @property
    def lap(self):
        return self._active_reader.lap

    @property
    def session(self):
        return self._active_reader.session

    @property
    def switch(self):
        return self._active_reader.switch

    @property
    def timing(self):
        return self._active_reader.timing

    @property
    def tyre(self):
        return self._active_reader.tyre

    @property
    def vehicle(self):
        return self._active_reader.vehicle

    @property
    def wheel(self):
        return self._active_reader.wheel
