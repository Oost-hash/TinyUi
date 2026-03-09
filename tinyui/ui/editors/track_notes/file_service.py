#
#  TinyUi - Track Notes File Service
#  Copyright (C) 2026 Oost-hash
#
#  This service handles file I/O specific to track/pace notes,
#  delegating low-level operations to the core FileService.
#

from typing import Any, Dict, List, Optional, Tuple

from ..core.file_service import FileService


class TrackNotesFileService:
    """
    Editor-specific file operations for track/pace notes.
    Uses core FileService for physical I/O and backend functions
    for format-specific loading/saving.
    """

    def __init__(self, file_service: FileService):
        """
        Initialize with a core FileService instance.
        """
        self._file_service = file_service

    def get_default_directory(self, notes_type: str) -> str:
        """
        Return the default directory path for the given notes type.
        Uses backend's set_file_path function.
        """
        from tinyui.backend.data import set_file_path

        return set_file_path(notes_type)

    def get_file_filter(self, notes_type: str) -> str:
        """
        Return the file filter string for the given notes type.
        Uses backend's set_notes_filter function.
        """
        from tinyui.backend.data import set_notes_filter

        return set_notes_filter(notes_type)

    def load_notes(
        self, filepath: str, filename: str, notes_type: str
    ) -> Optional[Tuple[List[Dict[str, Any]], Dict[str, Any]]]:
        """
        Load notes from a file.

        Args:
            filepath: Directory path (with trailing slash)
            filename: Name of the file
            notes_type: "Pace Notes" or "Track Notes"

        Returns:
            (entries, metadata) tuple if successful, else None.
        """
        from tinyui.backend.data import (
            load_notes_file,
            set_notes_filter,
            set_notes_header,
            set_notes_parser,
        )

        try:
            file_filter = set_notes_filter(notes_type)
            notes_header = set_notes_header(notes_type)
            result = load_notes_file(
                filepath=filepath,
                filename=filename,
                table_header=notes_header,
                parser=set_notes_parser(file_filter),
            )
            if result is None:
                return None
            entries, metadata = result
            return list(entries), dict(metadata) if metadata else {}
        except Exception as e:
            self._file_service.error_occurred.emit(f"Failed to load notes: {e}")
            return None

    def save_notes(
        self,
        filepath: str,
        filename: str,
        notes_type: str,
        entries: List[Dict[str, Any]],
        metadata: Dict[str, Any],
    ) -> bool:
        """
        Save notes to a file.

        Returns True if successful, False otherwise.
        """
        from tinyui.backend.data import (
            save_notes_file,
            set_notes_filter,
            set_notes_header,
            set_notes_writer,
        )

        try:
            file_filter = set_notes_filter(notes_type)
            notes_header = set_notes_header(notes_type)
            save_notes_file(
                filepath=filepath,
                filename=filename,
                table_header=notes_header,
                dataset=entries,
                metadata=metadata,
                writer=set_notes_writer(file_filter),
            )
            return True
        except Exception as e:
            self._file_service.error_occurred.emit(f"Failed to save notes: {e}")
            return False

    def create_default_metadata(self) -> Dict[str, Any]:
        """
        Create a default metadata dictionary.
        """
        from tinyui.backend.data import create_notes_metadata

        return create_notes_metadata()
