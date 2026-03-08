#
#  TinyUi - Track Info Editor ViewModel
#  Copyright (C) 2026 Oost-hash
#

from typing import Any, List, Optional

from ..core.base_viewmodel import BaseViewModel
from .service import TrackInfo, TrackInfoService


class TrackInfoEditorVM(BaseViewModel[TrackInfo]):
    """ViewModel for track info editor.

    Exposes track-specific operations including telemetry import
    and speed trap positioning.
    """

    def __init__(self, service: TrackInfoService):
        super().__init__(service)
        self._service: TrackInfoService = service

    def add_track(self, base_name: str = "") -> Optional[str]:
        """Add new track. Auto-imports current track name from telemetry.

        If telemetry provides a track name and it doesn't exist yet,
        uses that name. Otherwise falls back to generating a unique name.

        Returns the name of the added track, or None if track already exists.
        """
        # Try auto-import from telemetry
        if not base_name:
            telemetry_name = self._service.get_current_track_name()
            if telemetry_name and self._model and telemetry_name not in self._model:
                track = self._service.create_track(telemetry_name)
                self.add_item(telemetry_name, track.to_dict())
                return telemetry_name

        # Fallback: generate unique name
        name_base = base_name or "New Track"
        counter = 1
        name = f"{name_base} {counter}"

        while self._model and name in self._model:
            counter += 1
            name = f"{name_base} {counter}"

        track = self._service.create_track(name)
        self.add_item(name, track.to_dict())
        return name

    def set_speed_trap_from_telemetry(self, track_name: str) -> tuple[bool, str]:
        """Set speed trap position from current telemetry data.

        Returns (success, message) tuple for the view to display.
        """
        if not self._model or track_name not in self._model:
            return False, "Track not found"

        current_track = self._service.get_current_track_name()
        if track_name != current_track:
            return False, (
                f"Cannot set for {track_name}. "
                f"Only current track: {current_track}"
            )

        if self._service.is_in_pits():
            return False, "Cannot set position while in pit lane"

        position = self._service.get_speed_trap_from_telemetry()
        if position is None:
            return False, "Cannot read position from telemetry"

        self.update_value(track_name, "speed_trap", position)
        return True, f"Speed trap set at {position} for {track_name}"

    def update_track_field(self, track_name: str, field: str, value: Any):
        """Update a single field of a track."""
        self.update_value(track_name, field, value)

    def _validate(self) -> bool:
        """Validate all tracks before save."""
        if not self._model:
            return True

        tracks = {}
        for name, data in self._model.to_dict().items():
            if isinstance(data, TrackInfo):
                tracks[name] = data
            else:
                tracks[name] = TrackInfo.from_dict(name, data)

        is_valid, error = self._service.validate(tracks)

        if not is_valid:
            self.error_occurred.emit(error)

        return is_valid

    def get_row_data(self, key: str, item: Any) -> List[Any]:
        """Convert track data to table row format.

        Returns: [name, pit_entry, pit_exit, pit_speed, speed_trap, sunrise, sunset]
        """
        if isinstance(item, dict):
            return [
                key,
                item.get("pit_entry", 0.0),
                item.get("pit_exit", 0.0),
                item.get("pit_speed", 0.0),
                item.get("speed_trap", 0.0),
                item.get("sunrise", "06:00"),
                item.get("sunset", "20:00"),
            ]
        return [key, 0.0, 0.0, 0.0, 0.0, "06:00", "20:00"]
