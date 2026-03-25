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
"""StateMonitorViewModel — live source inspector for Dev Tools.

Supports two kinds of inspectable sources:
  - ConnectorSource  : polls dot-path attributes on a telemetry connector
  - QObjectSource    : reads all Qt-registered properties via QMetaObject

The UI shows a selector strip; picking a source refreshes the property table
below it at 200 ms.  Change detection per key drives the flash/heartbeat dot.
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from PySide6.QtCore import Property, QObject, QTimer, Signal, Slot

from tinycore.log import get_logger

if TYPE_CHECKING:
    from tinycore.session.runtime import SessionRuntime
    from tinycore.telemetry.registry import ConnectorRegistry

_log = get_logger(__name__)

# Properties inherited from QObject base that add noise; skip them.
_SKIP_PROPS = frozenset({"objectName"})


# ── Source types ──────────────────────────────────────────────────────────────


class _Source:
    def __init__(self, label: str) -> None:
        self.label = label

    def snapshot(self) -> list[tuple[str, str]]:
        raise NotImplementedError


class _ConnectorSource(_Source):
    """Reads dot-path attributes from a telemetry connector."""

    def __init__(self, label: str, connector, paths: list[str]) -> None:
        super().__init__(label)
        self._connector = connector
        self._paths = paths

    def snapshot(self) -> list[tuple[str, str]]:
        return [(path, self._read(path)) for path in self._paths]

    def _read(self, path: str) -> str:
        try:
            parts = path.split(".")
            obj = self._connector
            for part in parts[:-1]:
                obj = getattr(obj, part)
            val = getattr(obj, parts[-1])()
            try:
                return f"{float(val):.6g}"
            except (ValueError, TypeError):
                return str(val)
        except Exception as exc:
            return f"err: {exc}"


def _binding_for_source(session: "SessionRuntime", consumer_name: str, capability: str):
    """Resolve one provider binding for the state monitor."""
    bindings = session.bindings_for(consumer_name)
    if capability:
        return bindings.get(capability)
    if len(bindings.resolved) == 1:
        return next(iter(bindings.resolved.values()))
    return None


_STATE_FIELDS: list[tuple[str, object]] = [
    # ── State ───────────────────────────────────────────────────────────────
    ("state.active", lambda c: str(c.state.active())),
    ("state.paused", lambda c: str(c.state.paused())),
    ("state.version", lambda c: c.state.version()),
    # ── Session ──────────────────────────────────────────────────────────────
    ("session.track", lambda c: c.session.track_name()),
    ("session.type", lambda c: str(c.session.session_type())),
    ("session.in_race", lambda c: str(c.session.in_race())),
    ("session.elapsed", lambda c: f"{c.session.elapsed():.1f} s"),
    ("session.remaining", lambda c: f"{c.session.remaining():.1f} s"),
    ("session.t_track", lambda c: f"{c.session.track_temperature():.1f} °C"),
    ("session.t_amb", lambda c: f"{c.session.ambient_temperature():.1f} °C"),
    ("session.raininess", lambda c: f"{c.session.raininess():.2f}"),
    # ── Vehicle ──────────────────────────────────────────────────────────────
    ("vehicle.player_idx", lambda c: str(c.vehicle.player_index())),
    ("vehicle.total", lambda c: str(c.vehicle.total_vehicles())),
    ("vehicle.driver", lambda c: c.vehicle.driver_name()),
    ("vehicle.car", lambda c: c.vehicle.vehicle_name()),
    ("vehicle.class", lambda c: c.vehicle.class_name()),
    ("vehicle.place", lambda c: str(c.vehicle.place())),
    ("vehicle.in_pits", lambda c: str(c.vehicle.in_pits())),
    ("vehicle.fuel", lambda c: f"{c.vehicle.fuel():.2f} L"),
    ("vehicle.speed", lambda c: f"{c.vehicle.speed() * 3.6:.1f} km/h"),
    (
        "vehicle.position",
        lambda c: (
            f"({c.vehicle.position_xyz()[0]:.2f}, {c.vehicle.position_xyz()[1]:.2f}, {c.vehicle.position_xyz()[2]:.2f})"
        ),
    ),
    # ── Lap ──────────────────────────────────────────────────────────────────
    ("lap.number", lambda c: str(c.lap.number())),
    ("lap.completed", lambda c: str(c.lap.completed_laps())),
    ("lap.distance", lambda c: f"{c.lap.distance():.1f} m"),
    ("lap.track_length", lambda c: f"{c.lap.track_length():.1f} m"),
    ("lap.progress", lambda c: f"{c.lap.progress() * 100:.1f} %"),
    ("lap.sector_index", lambda c: str(c.lap.sector_index())),
    # ── Engine ─────────────────────────────────────────────────────────────────
    ("engine.gear", lambda c: str(c.engine.gear())),
    ("engine.gear_max", lambda c: str(c.engine.gear_max())),
    ("engine.rpm", lambda c: f"{c.engine.rpm():.0f}"),
    ("engine.rpm_max", lambda c: f"{c.engine.rpm_max():.0f}"),
    ("engine.torque", lambda c: f"{c.engine.torque():.2f} Nm"),
    ("engine.turbo", lambda c: f"{c.engine.turbo():.3f} bar"),
    ("engine.temp_oil", lambda c: f"{c.engine.oil_temperature():.1f} °C"),
    ("engine.temp_water", lambda c: f"{c.engine.water_temperature():.1f} °C"),
    # ── Electric Motor ──────────────────────────────────────────────────────
    ("emotor.state", lambda c: str(c.electric_motor.state())),
    ("emotor.battery", lambda c: f"{c.electric_motor.battery_charge():.2f}"),
    ("emotor.rpm", lambda c: f"{c.electric_motor.rpm():.0f}"),
    ("emotor.torque", lambda c: f"{c.electric_motor.torque():.2f} Nm"),
    ("emotor.temp_motor", lambda c: f"{c.electric_motor.motor_temperature():.1f} °C"),
    ("emotor.temp_water", lambda c: f"{c.electric_motor.water_temperature():.1f} °C"),
    # ── Inputs ───────────────────────────────────────────────────────────────
    ("inputs.throttle", lambda c: f"{c.inputs.throttle():.3f}"),
    ("inputs.throttle_raw", lambda c: f"{c.inputs.throttle_raw():.3f}"),
    ("inputs.brake", lambda c: f"{c.inputs.brake():.3f}"),
    ("inputs.brake_raw", lambda c: f"{c.inputs.brake_raw():.3f}"),
    ("inputs.clutch", lambda c: f"{c.inputs.clutch():.3f}"),
    ("inputs.steering", lambda c: f"{c.inputs.steering():.4f}"),
    ("inputs.steering_raw", lambda c: f"{c.inputs.steering_raw():.4f}"),
    ("inputs.ffb", lambda c: f"{c.inputs.force_feedback():.3f} Nm"),
    # ── Brake ─────────────────────────────────────────────────────────────────
    ("brake.bias_front", lambda c: f"{c.brake.bias_front():.3f}"),
    ("brake.pressure_fl", lambda c: f"{c.brake.pressure()[0]:.3f}"),
    ("brake.pressure_fr", lambda c: f"{c.brake.pressure()[1]:.3f}"),
    ("brake.pressure_rl", lambda c: f"{c.brake.pressure()[2]:.3f}"),
    ("brake.pressure_rr", lambda c: f"{c.brake.pressure()[3]:.3f}"),
    ("brake.temp_fl", lambda c: f"{c.brake.temperature()[0]:.1f} °C"),
    ("brake.temp_fr", lambda c: f"{c.brake.temperature()[1]:.1f} °C"),
    ("brake.temp_rl", lambda c: f"{c.brake.temperature()[2]:.1f} °C"),
    ("brake.temp_rr", lambda c: f"{c.brake.temperature()[3]:.1f} °C"),
    ("brake.wear_fl", lambda c: f"{c.brake.wear()[0]:.3f}"),
    ("brake.wear_fr", lambda c: f"{c.brake.wear()[1]:.3f}"),
    ("brake.wear_rl", lambda c: f"{c.brake.wear()[2]:.3f}"),
    ("brake.wear_rr", lambda c: f"{c.brake.wear()[3]:.3f}"),
    # ── Tyre ──────────────────────────────────────────────────────────────────
    ("tyre.compound_f", lambda c: str(c.tyre.compound()[0])),
    ("tyre.compound_r", lambda c: str(c.tyre.compound()[1])),
    ("tyre.compound_name_f", lambda c: c.tyre.compound_name()[0]),
    ("tyre.compound_name_r", lambda c: c.tyre.compound_name()[1]),
    ("tyre.temp_surface_fl", lambda c: f"{c.tyre.surface_temperature()[0]:.1f} °C"),
    ("tyre.temp_surface_fr", lambda c: f"{c.tyre.surface_temperature()[1]:.1f} °C"),
    ("tyre.temp_surface_rl", lambda c: f"{c.tyre.surface_temperature()[2]:.1f} °C"),
    ("tyre.temp_surface_rr", lambda c: f"{c.tyre.surface_temperature()[3]:.1f} °C"),
    ("tyre.temp_inner_fl", lambda c: f"{c.tyre.inner_temperature()[0]:.1f} °C"),
    ("tyre.temp_inner_fr", lambda c: f"{c.tyre.inner_temperature()[1]:.1f} °C"),
    ("tyre.temp_inner_rl", lambda c: f"{c.tyre.inner_temperature()[2]:.1f} °C"),
    ("tyre.temp_inner_rr", lambda c: f"{c.tyre.inner_temperature()[3]:.1f} °C"),
    ("tyre.pressure_fl", lambda c: f"{c.tyre.pressure()[0]:.2f}"),
    ("tyre.pressure_fr", lambda c: f"{c.tyre.pressure()[1]:.2f}"),
    ("tyre.pressure_rl", lambda c: f"{c.tyre.pressure()[2]:.2f}"),
    ("tyre.pressure_rr", lambda c: f"{c.tyre.pressure()[3]:.2f}"),
    ("tyre.wear_fl", lambda c: f"{c.tyre.wear()[0]:.3f}"),
    ("tyre.wear_fr", lambda c: f"{c.tyre.wear()[1]:.3f}"),
    ("tyre.wear_rl", lambda c: f"{c.tyre.wear()[2]:.3f}"),
    ("tyre.wear_rr", lambda c: f"{c.tyre.wear()[3]:.3f}"),
    ("tyre.load_fl", lambda c: f"{c.tyre.load()[0]:.1f} N"),
    ("tyre.load_fr", lambda c: f"{c.tyre.load()[1]:.1f} N"),
    ("tyre.load_rl", lambda c: f"{c.tyre.load()[2]:.1f} N"),
    ("tyre.load_rr", lambda c: f"{c.tyre.load()[3]:.1f} N"),
    # ── Wheel ─────────────────────────────────────────────────────────────────
    ("wheel.camber_fl", lambda c: f"{c.wheel.camber()[0]:.3f} rad"),
    ("wheel.camber_fr", lambda c: f"{c.wheel.camber()[1]:.3f} rad"),
    ("wheel.camber_rl", lambda c: f"{c.wheel.camber()[2]:.3f} rad"),
    ("wheel.camber_rr", lambda c: f"{c.wheel.camber()[3]:.3f} rad"),
    ("wheel.rotation_fl", lambda c: f"{c.wheel.rotation()[0]:.3f} rad"),
    ("wheel.rotation_fr", lambda c: f"{c.wheel.rotation()[1]:.3f} rad"),
    ("wheel.rotation_rl", lambda c: f"{c.wheel.rotation()[2]:.3f} rad"),
    ("wheel.rotation_rr", lambda c: f"{c.wheel.rotation()[3]:.3f} rad"),
    ("wheel.ride_height_fl", lambda c: f"{c.wheel.ride_height()[0]:.1f} mm"),
    ("wheel.ride_height_fr", lambda c: f"{c.wheel.ride_height()[1]:.1f} mm"),
    ("wheel.ride_height_rl", lambda c: f"{c.wheel.ride_height()[2]:.1f} mm"),
    ("wheel.ride_height_rr", lambda c: f"{c.wheel.ride_height()[3]:.1f} mm"),
    ("wheel.susp_defl_fl", lambda c: f"{c.wheel.suspension_deflection()[0]:.1f} mm"),
    ("wheel.susp_defl_fr", lambda c: f"{c.wheel.suspension_deflection()[1]:.1f} mm"),
    ("wheel.susp_defl_rl", lambda c: f"{c.wheel.suspension_deflection()[2]:.1f} mm"),
    ("wheel.susp_defl_rr", lambda c: f"{c.wheel.suspension_deflection()[3]:.1f} mm"),
    # ── Switch ───────────────────────────────────────────────────────────────
    ("switch.headlights", lambda c: str(c.switch.headlights())),
    ("switch.speed_limiter", lambda c: str(c.switch.speed_limiter())),
    ("switch.drs", lambda c: str(c.switch.drs_status())),
    # ── Timing ───────────────────────────────────────────────────────────────
    ("timing.current_lap", lambda c: f"{c.timing.current_laptime():.3f} s"),
    ("timing.last_lap", lambda c: f"{c.timing.last_laptime():.3f} s"),
    ("timing.best_lap", lambda c: f"{c.timing.best_laptime():.3f} s"),
    ("timing.cur_s1", lambda c: f"{c.timing.current_sector1():.3f} s"),
    ("timing.cur_s2", lambda c: f"{c.timing.current_sector2():.3f} s"),
    ("timing.last_s1", lambda c: f"{c.timing.last_sector1():.3f} s"),
    ("timing.last_s2", lambda c: f"{c.timing.last_sector2():.3f} s"),
    ("timing.best_s1", lambda c: f"{c.timing.best_sector1():.3f} s"),
    ("timing.best_s2", lambda c: f"{c.timing.best_sector2():.3f} s"),
    ("timing.behind_leader", lambda c: f"{c.timing.behind_leader():.3f} s"),
]


class _ConnectorStateSource(_Source):
    """Shows full connector state: active/session/vehicle/lap/engine."""

    def __init__(self, label: str, connector) -> None:
        super().__init__(label)
        self._connector = connector

    def snapshot(self) -> list[tuple[str, str]]:
        result = []
        for key, getter in _STATE_FIELDS:
            try:
                val = getter(self._connector)  # type: ignore[operator]
            except Exception as exc:
                val = f"err: {exc}"
            result.append((key, val))
        return result


class _QObjectSource(_Source):
    """Reads all Qt-registered properties from a QObject via QMetaObject."""

    def __init__(self, label: str, obj: QObject) -> None:
        super().__init__(label)
        self._obj = obj

    def snapshot(self) -> list[tuple[str, str]]:
        meta = self._obj.metaObject()
        result = []
        for i in range(meta.propertyCount()):
            prop = meta.property(i)
            name = prop.name()
            if name in _SKIP_PROPS:
                continue
            try:
                val = prop.read(self._obj)
                if isinstance(val, list):
                    result.append((name, f"[{len(val)} items]"))
                elif isinstance(val, dict):
                    result.append((name, "{…}"))
                else:
                    try:
                        result.append((name, f"{float(val):.6g}"))
                    except (ValueError, TypeError):
                        result.append((name, str(val)))
            except Exception as exc:
                result.append((name, f"err: {exc}"))
        return result


# ── ViewModel ─────────────────────────────────────────────────────────────────


class StateMonitorViewModel(QObject):
    """Exposes a selectable set of live sources to QML.

    Usage::

        vm = StateMonitorViewModel()
        vm.setup(connectors, session, [("demo", "", "vehicle.fuel"), ...])
        vm.register_object("Widget: Fuel", fuel_ctx)
        # pass vm via extra_context; call vm.start() in pre_run
    """

    sourcesChanged = Signal()
    selectedChanged = Signal()
    entriesChanged = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._sources: list[_Source] = []
        self._selected: int = -1
        self._prev: dict[str, str] = {}
        self._changed_at: dict[str, int] = {}
        self._entries: list[dict] = []
        self._timer = QTimer(self)
        self._timer.setInterval(200)
        self._timer.timeout.connect(self._refresh)

    # ── Registration ──────────────────────────────────────────────────────────

    def register_object(self, label: str, obj: QObject) -> None:
        """Register a QObject for live property inspection."""
        self._sources.append(_QObjectSource(label, obj))
        if self._selected < 0:
            self._selected = 0
        self.sourcesChanged.emit()

    def setup(
        self,
        connectors: ConnectorRegistry,
        session: "SessionRuntime",
        sources: list[tuple[str, str, str]],
    ) -> None:
        """Register provider-backed dot-path sources, grouped by consumer plugin."""
        by_consumer: dict[str, dict[str, list[str]]] = {}
        for consumer_name, capability, path in sources:
            by_consumer.setdefault(consumer_name, {}).setdefault(capability, []).append(path)

        for consumer_name, paths_by_capability in by_consumer.items():
            seen_provider_names: set[str] = set()

            for capability, paths in paths_by_capability.items():
                binding = _binding_for_source(session, consumer_name, capability)
                if binding is None:
                    continue

                if binding.provider_name not in seen_provider_names:
                    connector = connectors.get(binding.provider_name)
                    if connector is not None:
                        self._sources.append(
                            _ConnectorStateSource(f"State: {binding.provider_name}", connector)
                        )
                        seen_provider_names.add(binding.provider_name)

                self._sources.append(
                    _ConnectorSource(
                        f"Polling: {consumer_name}"
                        + (f" [{capability}]" if capability else ""),
                        binding.provider,
                        paths,
                    )
                )

        if self._selected < 0 and self._sources:
            self._selected = 0
        self.sourcesChanged.emit()
        _log.info("state monitor setup: %d sources", len(self._sources))

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def start(self) -> None:
        """Start polling.  Must be called after QApplication is created."""
        self._timer.start()

    def shutdown(self) -> None:
        self._timer.stop()

    # ── Internal ──────────────────────────────────────────────────────────────

    def _refresh(self) -> None:
        if not self._sources or self._selected < 0:
            return

        snapshot = self._sources[self._selected].snapshot()
        entries = []
        changed_any = False
        now_ms = int(time.time() * 1000)

        for key, value in snapshot:
            changed = value != self._prev.get(key)
            if changed:
                changed_any = True
                self._prev[key] = value
                self._changed_at[key] = now_ms

            entries.append(
                {
                    "key": key,
                    "value": value,
                    "changed": changed,
                    "changedAt": self._changed_at.get(key, 0),
                }
            )

        self._entries = entries
        if changed_any:
            self.entriesChanged.emit()

    # ── QML properties ────────────────────────────────────────────────────────

    @Property("QVariantList", notify=sourcesChanged)
    def sources(self) -> list:
        """List of ``{label, index}`` for the source selector."""
        return [{"label": s.label, "index": i} for i, s in enumerate(self._sources)]

    @Property(int, notify=selectedChanged)
    def selectedIndex(self) -> int:
        return self._selected

    @Slot(int)
    def selectSource(self, index: int) -> None:
        if 0 <= index < len(self._sources) and index != self._selected:
            self._selected = index
            # Reset change tracking so the new source starts clean
            self._prev.clear()
            self._changed_at.clear()
            self._entries = []
            self.selectedChanged.emit()
            self.entriesChanged.emit()

    @Property("QVariantList", notify=entriesChanged)
    def entries(self) -> list:
        return self._entries
