# editors/brake/__init__.py


def create_brake_editor(parent=None):
    """
    Factory for brake editor.
    Wires up all components with proper dependencies.
    Lazy imports to avoid triggering backend at import time.
    """
    from ..core.store_adapter import ConfigStoreAdapter
    from .service import BrakeService
    from .view import BrakeEditorView
    from .viewmodel import BrakeEditorVM

    # 1. Data layer
    store = ConfigStoreAdapter()

    # 2. Service layer
    service = BrakeService(store_adapter=store)

    # 3. ViewModel layer
    viewmodel = BrakeEditorVM(service)

    # 4. View layer
    view = BrakeEditorView(parent)
    view.bind_to(viewmodel)

    return view
