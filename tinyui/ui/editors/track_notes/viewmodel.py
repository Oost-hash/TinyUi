#
#  TinyUi - Track Notes ViewModel
#  Copyright (C) 2026 Oost-hash
#
#  ViewModel for track/pace notes editor.
#  Manages state and communicates with service.
#

from typing import Any, Dict, List, Optional, Set

from PySide2.QtCore import QObject, Signal

from .service import TrackNotes, TrackNotesService


class TrackNotesEditorVM(QObject):
    """
    ViewModel for track notes editor.
    Manual dirty tracking (list data, no ObservableDict).
    """

    # Signals
    data_changed = Signal()  # Entries changed
    modified_changed = Signal(bool)  # Dirty state
    error_occurred = Signal(str)
    operation_completed = Signal(str)
    notes_type_changed = Signal(str)  # Pace vs Track
    filename_changed = Signal(str)
    positions_changed = Signal(set)  # For MapView

    def __init__(self, service: TrackNotesService):
        super().__init__()
        self._service = service
        self._notes: Optional[TrackNotes] = None
        self._is_modified = False
        self._decimals = 2

    @property
    def notes_type(self) -> str:
        return self._notes.notes_type if self._notes else ""

    @property
    def filename(self) -> str:
        return self._notes.filename if self._notes else ""

    @property
    def entries(self) -> List[Dict[str, Any]]:
        return self._notes.entries if self._notes else []

    @property
    def positions(self) -> Set[float]:
        """Set of distances for MapView markers."""
        if not self._notes:
            return set()
        return {entry.get("distance", 0.0) for entry in self._notes.entries}

    @property
    def is_modified(self) -> bool:
        return self._is_modified

    @property
    def metadata(self) -> Dict[str, Any]:
        return self._notes.metadata if self._notes else {}

    def _mark_dirty(self):
        if not self._is_modified:
            self._is_modified = True
            self.modified_changed.emit(True)

    def mark_clean(self):
        self._is_modified = False
        self.modified_changed.emit(False)

    # --- New: File dialog helper ---
    def get_file_dialog_info(self, notes_type: str) -> tuple[str, str]:
        """
        Return (default_directory, file_filter) for the given notes type.
        Used by view to configure QFileDialog.
        """
        if not self._service:
            return "", ""
        return (
            self._service._file_service.get_default_directory(notes_type),
            self._service._file_service.get_file_filter(notes_type),
        )

    # --- File operations ---

    def new_file(self, notes_type: str, filename: str = ""):
        """Create new empty notes file."""
        if not filename:
            filename = self._service.get_track_name() or ""

        self._notes = self._service.create_empty(notes_type, filename)
        self._is_modified = True
        self.notes_type_changed.emit(notes_type)
        self.filename_changed.emit(filename)
        self.data_changed.emit()
        self.positions_changed.emit(self.positions)

    def load_file(self, filepath: str, filename: str, notes_type: str) -> bool:
        """Load notes from file."""
        notes = self._service.load(filepath, filename, notes_type)

        if notes is None:
            self.error_occurred.emit("Cannot open selected file. Invalid notes file.")
            return False

        self._notes = notes
        self.mark_clean()
        self.notes_type_changed.emit(notes.notes_type)
        self.filename_changed.emit(notes.filename)
        self.data_changed.emit()
        self.positions_changed.emit(self.positions)
        return True

    def save_file(self, filepath: str) -> bool:
        """Save notes to file."""
        if not self._notes:
            self.error_occurred.emit("Nothing to save")
            return False

        # Validate
        is_valid, error = self._service.validate(self._notes)
        if not is_valid:
            self.error_occurred.emit(error)
            return False

        # Sort before save
        self.sort_entries()

        # Persist
        success = self._service.save(self._notes, filepath)

        if success:
            self.mark_clean()
            self.operation_completed.emit(
                f"Notes saved at: {filepath}{self._notes.filename}"
            )

        return success

    # --- Entry CRUD ---

    def add_entry(self, position: Optional[float] = None) -> int:
        """Add new entry at position or at end."""
        if not self._notes:
            return -1

        if position is None:
            # Auto position: max + 100, or 0
            if self._notes.entries:
                position = (
                    max(e.get("distance", 0.0) for e in self._notes.entries) + 100.0
                )
            else:
                position = 0.0

        # Default entry struct based on type
        if self._notes.notes_type == "Pace Notes":
            entry = {
                "distance": round(position, self._decimals),
                "note": "",
                "call": "",
            }
        else:
            entry = {"distance": round(position, self._decimals), "note": ""}

        self._notes.entries.append(entry)
        self._mark_dirty()
        self.data_changed.emit()
        self.positions_changed.emit(self.positions)
        return len(self._notes.entries) - 1  # Index of new entry

    def insert_entry(self, index: int, position: Optional[float] = None) -> int:
        """Insert entry at specific index."""
        if not self._notes or index < 0 or index > len(self._notes.entries):
            return self.add_entry(position)

        if position is None:
            # Use neighbor distance or 0
            if index < len(self._notes.entries):
                position = self._notes.entries[index].get("distance", 0.0)
            else:
                position = 0.0

        if self._notes.notes_type == "Pace Notes":
            entry = {
                "distance": round(position, self._decimals),
                "note": "",
                "call": "",
            }
        else:
            entry = {"distance": round(position, self._decimals), "note": ""}

        self._notes.entries.insert(index, entry)
        self._mark_dirty()
        self.data_changed.emit()
        self.positions_changed.emit(self.positions)
        return index

    def update_entry(self, index: int, field: str, value: Any):
        """Update single field of entry."""
        if not self._notes or index < 0 or index >= len(self._notes.entries):
            return

        entry = self._notes.entries[index]
        old_value = entry.get(field)

        if field == "distance":
            try:
                value = round(float(value), self._decimals)
            except ValueError:
                return

        entry[field] = value
        self._mark_dirty()
        self.data_changed.emit()

        # If distance changed, update positions
        if field == "distance" and old_value != value:
            self.positions_changed.emit(self.positions)

    def delete_entries(self, indices: List[int]):
        """Delete entries by indices."""
        if not self._notes:
            return

        # Sort descending to avoid index shifting
        for idx in sorted(indices, reverse=True):
            if 0 <= idx < len(self._notes.entries):
                del self._notes.entries[idx]

        self._mark_dirty()
        self.data_changed.emit()
        self.positions_changed.emit(self.positions)

    def sort_entries(self):
        """Sort by distance ascending."""
        if not self._notes or len(self._notes.entries) < 2:
            return

        self._notes.entries.sort(key=lambda e: e.get("distance", 0.0))
        self.data_changed.emit()

    # --- Batch operations ---

    def apply_offset(self, indices: List[int], offset: float, is_scale: bool = False):
        """Apply offset or scale to selected entries."""
        if not self._notes:
            return

        for idx in indices:
            if 0 <= idx < len(self._notes.entries):
                entry = self._notes.entries[idx]
                current = entry.get("distance", 0.0)

                if is_scale:
                    new_val = current * offset
                else:
                    new_val = current + offset

                entry["distance"] = round(new_val, self._decimals)

        self.sort_entries()  # Re-sort after offset
        self._mark_dirty()
        self.positions_changed.emit(self.positions)

    # --- Telemetry ---

    def get_position_from_telemetry(self) -> Optional[float]:
        """Get current position from API."""
        return self._service.get_distance_from_telemetry()

    def get_track_name(self) -> Optional[str]:
        """Get track name from API."""
        return self._service.get_track_name()

    # --- Metadata ---

    def update_metadata(self, key: str, value: Any):
        """Update metadata field."""
        if self._notes:
            self._notes.metadata[key] = value
            self._mark_dirty()

    def get_row_data(self, index: int) -> List[Any]:
        """Format entry for table display."""
        if not self._notes or index >= len(self._notes.entries):
            return []

        entry = self._notes.entries[index]

        if self._notes.notes_type == "Pace Notes":
            return [
                entry.get("distance", 0.0),
                entry.get("note", ""),
                entry.get("call", ""),
            ]
        else:
            return [entry.get("distance", 0.0), entry.get("note", "")]
