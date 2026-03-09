#
#  TinyUi - Track Notes Service
#  Copyright (C) 2026 Oost-hash
#
#  Service layer for track/pace notes editor.
#  Handles domain logic, validation, and telemetry integration.
#

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..core.editor_service import EditorService
from .file_service import TrackNotesFileService


@dataclass
class TrackNotes:
    """Domain model for track/pace notes."""

    notes_type: str  # "Pace Notes" or "Track Notes"
    filename: str
    entries: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def copy(self) -> "TrackNotes":
        """Deep copy of notes."""
        import copy

        return TrackNotes(
            notes_type=self.notes_type,
            filename=self.filename,
            entries=copy.deepcopy(self.entries),
            metadata=copy.deepcopy(self.metadata),
        )


class TrackNotesService(EditorService[TrackNotes]):
    """
    Service for track notes editor.
    Handles domain logic, validation, telemetry API integration,
    and delegates file I/O to TrackNotesFileService.
    """

    def __init__(self, file_service: TrackNotesFileService):
        # No store adapter or schema – file-based persistence
        super().__init__(store_adapter=None, schema=None)
        self._file_service = file_service
        self._cfg_attr = None
        self._cfg_type = None

    def load(
        self, filepath: str, filename: str, notes_type: str
    ) -> Optional[TrackNotes]:
        """
        Load notes from a file.
        Delegates to file service and converts result to domain model.
        """
        self.load_started.emit()

        try:
            result = self._file_service.load_notes(filepath, filename, notes_type)
            if result is None:
                self.load_failed.emit("Invalid notes file")
                return None

            entries, metadata = result

            notes = TrackNotes(
                notes_type=notes_type,
                filename=filename,
                entries=list(entries),
                metadata=metadata or self._file_service.create_default_metadata(),
            )

            self._cache = notes
            self.load_completed.emit(notes)
            return notes

        except Exception as e:
            self.load_failed.emit(str(e))
            return None

    def save(self, notes: TrackNotes, filepath: str) -> bool:
        """
        Save notes to a file.
        Delegates to file service.
        """
        self.save_started.emit()

        try:
            success = self._file_service.save_notes(
                filepath=filepath,
                filename=notes.filename,
                notes_type=notes.notes_type,
                entries=notes.entries,
                metadata=notes.metadata,
            )

            if success:
                self.save_completed.emit()
            else:
                self.save_failed.emit("Save failed")
            return success

        except Exception as e:
            self.save_failed.emit(str(e))
            return False

    def validate(self, notes: TrackNotes) -> tuple[bool, Optional[str]]:
        """Validate notes before save."""
        if not notes.entries:
            return False, "Nothing to save"

        if not notes.filename:
            return False, "Filename required"

        # Check for duplicate distances
        seen = set()
        for entry in notes.entries:
            dist = entry.get("distance")
            if dist in seen:
                return False, f"Duplicate distance: {dist}"
            seen.add(dist)

        return True, None

    def get_distance_from_telemetry(self) -> Optional[float]:
        """Get current lap distance from API."""
        try:
            from tinyui.backend.controls import api

            return api.read.lap.distance()
        except Exception:
            return None

    def get_track_name(self) -> Optional[str]:
        """Get current track name from API."""
        try:
            from tinyui.backend.controls import api

            return api.read.session.track_name()
        except Exception:
            return None

    def create_empty(self, notes_type: str, filename: str = "") -> TrackNotes:
        """Create new empty notes."""
        # Create a single default entry
        if notes_type == "Pace Notes":
            entries = [{"distance": 0.0, "note": "", "call": ""}]
        else:
            entries = [{"distance": 0.0, "note": ""}]

        return TrackNotes(
            notes_type=notes_type,
            filename=filename,
            entries=entries,
            metadata=self._file_service.create_default_metadata(),
        )

    def get_default_directory(self, notes_type: str) -> str:
        """Get default directory for the given notes type."""
        return self._file_service.get_default_directory(notes_type)

    def get_file_filter(self, notes_type: str) -> str:
        """Get file filter for the given notes type."""
        return self._file_service.get_file_filter(notes_type)
