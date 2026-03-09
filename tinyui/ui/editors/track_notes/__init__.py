#
#  TinyUi - Track Notes Editor Factory
#  Copyright (C) 2026 Oost-hash
#
#  Factory creates all dependencies and assembles the editor.
#

from ..core.file_service import FileService
from .file_service import TrackNotesFileService
from .service import TrackNotesService
from .view import TrackNotesEditorView
from .viewmodel import TrackNotesEditorVM


def create_track_notes_editor(parent=None):
    # 1. Core file service
    core_fs = FileService()

    # 2. Editor-specific file service
    track_fs = TrackNotesFileService(core_fs)

    # 3. Domain service
    service = TrackNotesService(track_fs)

    # 4. ViewModel
    viewmodel = TrackNotesEditorVM(service)

    # 5. View
    view = TrackNotesEditorView(parent)

    # 6. Bind viewmodel and core file service
    view.bind_to(viewmodel, core_fs)

    return view
