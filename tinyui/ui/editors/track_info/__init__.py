# editors/track_info/__init__.py


def create_track_info_editor(parent=None):
    """
    Factory for track info editor.
    Wires up all components with proper dependencies.
    Lazy imports to avoid triggering backend at import time.
    """
    from ..core.store_adapter import ConfigStoreAdapter
    from .service import TrackInfoService
    from .viewmodel import TrackInfoEditorVM

    # 1. Data layer
    store = ConfigStoreAdapter()

    # 2. Service layer
    service = TrackInfoService(store_adapter=store)

    # 3. ViewModel layer
    viewmodel = TrackInfoEditorVM(service)

    # Note: View not yet implemented (will be done when UI migration happens)
    return viewmodel
