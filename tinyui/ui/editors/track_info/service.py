#
#  TinyUi - Track Info Editor Service
#  Copyright (C) 2026 Oost-hash
#

from dataclasses import dataclass
from typing import Any, Dict, Optional

from ..core.editor_service import EditorService


@dataclass
class TrackInfo:
    """Domain model for track information.

    Fields:
        name: Track name (key).
        pit_entry: Pit entry position in metres.
        pit_exit: Pit exit position in metres.
        pit_speed: Pit lane speed limit in m/s.
        speed_trap: Speed trap position in metres.
        sunrise: Sunrise time string (HH:MM).
        sunset: Sunset time string (HH:MM).
    """

    name: str
    pit_entry: float = 0.0
    pit_exit: float = 0.0
    pit_speed: float = 0.0
    speed_trap: float = 0.0
    sunrise: str = "06:00"
    sunset: str = "20:00"

    def to_dict(self) -> dict:
        return {
            "pit_entry": self.pit_entry,
            "pit_exit": self.pit_exit,
            "pit_speed": self.pit_speed,
            "speed_trap": self.speed_trap,
            "sunrise": self.sunrise,
            "sunset": self.sunset,
        }

    @classmethod
    def from_dict(cls, name: str, data: dict) -> "TrackInfo":
        return cls(
            name=name,
            pit_entry=data.get("pit_entry", 0.0),
            pit_exit=data.get("pit_exit", 0.0),
            pit_speed=data.get("pit_speed", 0.0),
            speed_trap=data.get("speed_trap", 0.0),
            sunrise=data.get("sunrise", "06:00"),
            sunset=data.get("sunset", "20:00"),
        )


class TrackInfoService(EditorService[TrackInfo]):
    """Service for track info editor.

    Handles persistence, telemetry import, and validation.
    """

    def __init__(self, store_adapter: Any):
        super().__init__(store_adapter, schema=None)
        self._cfg_attr = "tracks"
        self._cfg_type = None  # Lazy loaded

    @property
    def cfg_type(self):
        if self._cfg_type is None:
            from tinyui.backend.constants import ConfigType
            self._cfg_type = ConfigType.TRACKS
        return self._cfg_type

    def load(self) -> Dict[str, TrackInfo]:
        """Load tracks from store and convert to domain models."""
        self.load_started.emit()

        try:
            raw_data = self._store.load(self._cfg_attr)
            models = {
                name: TrackInfo.from_dict(name, data)
                for name, data in raw_data.items()
            }
            self._cache = models
            self.load_completed.emit(models)
            return models

        except Exception as e:
            self.load_failed.emit(str(e))
            return {}

    def save(self, data: Dict[str, TrackInfo]) -> bool:
        """Validate and save track data."""
        self.save_started.emit()

        is_valid, error = self.validate(data)
        if not is_valid:
            self.save_failed.emit(error)
            return False

        raw_data = {name: track.to_dict() for name, track in data.items()}

        try:
            self._store.save(self._cfg_attr, self.cfg_type, raw_data)
            self.save_completed.emit()
            return True

        except Exception as e:
            self.save_failed.emit(str(e))
            return False

    def validate(self, data: Dict[str, TrackInfo]) -> tuple[bool, Optional[str]]:
        """Validate track data."""
        for name, track in data.items():
            if track.pit_entry < 0:
                return False, f"{name}: pit entry cannot be negative"
            if track.pit_exit < 0:
                return False, f"{name}: pit exit cannot be negative"
            if track.pit_speed < 0:
                return False, f"{name}: pit speed cannot be negative"
            if track.speed_trap < 0:
                return False, f"{name}: speed trap cannot be negative"
        return True, None

    def get_current_track_name(self) -> Optional[str]:
        """Get current track name from telemetry API."""
        try:
            from tinyui.backend.controls import api
            name = api.read.session.track_name()
            return name if name else None
        except Exception:
            return None

    def get_speed_trap_from_telemetry(self) -> Optional[float]:
        """Read current lap distance from telemetry for speed trap position."""
        try:
            from tinyui.backend.controls import api

            if api.read.vehicle.in_pits():
                return None

            return round(api.read.lap.distance(), 4)
        except Exception:
            return None

    def is_in_pits(self) -> bool:
        """Check if vehicle is currently in pit lane."""
        try:
            from tinyui.backend.controls import api
            return api.read.vehicle.in_pits()
        except Exception:
            return False

    def create_track(self, name: str) -> TrackInfo:
        """Create new track with defaults."""
        return TrackInfo(name=name)
