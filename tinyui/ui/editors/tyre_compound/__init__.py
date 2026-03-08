# editors/tyre_compound/__init__.py


def create_tyre_compound_editor(parent=None):
    """
    Factory for tyre compound editor.
    Lazy imports to avoid triggering backend at import time.
    """
    from ..core.store_adapter import ConfigStoreAdapter
    from .service import TyreCompoundService
    from .view import TyreCompoundEditorView
    from .viewmodel import TyreCompoundEditorVM

    service = TyreCompoundService(store_adapter=ConfigStoreAdapter())
    viewmodel = TyreCompoundEditorVM(service)
    view = TyreCompoundEditorView(parent)
    view.bind_to(viewmodel)
    return view
