# editors/heatmap/__init__.py


def create_heatmap_editor(parent=None):
    """
    Factory for heatmap editor.
    Wires up all components with proper dependencies.
    """
    from ..core.store_adapter import ConfigStoreAdapter
    from .service import HeatmapService
    from .view import HeatmapEditorView
    from .viewmodel import HeatmapEditorVM

    # 1. Data layer
    store = ConfigStoreAdapter()

    # 2. Service layer
    service = HeatmapService(store_adapter=store)

    # 3. ViewModel layer
    viewmodel = HeatmapEditorVM(service)

    # 4. View layer
    view = HeatmapEditorView(parent)
    view.bind_to(viewmodel)

    return view
