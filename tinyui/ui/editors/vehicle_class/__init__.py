# editors/vehicle_class/__init__.py


def create_vehicle_class_editor(parent=None):
    """
    Factory for vehicle class editor.
    Lazy imports to avoid triggering backend at import time.
    """
    from ..core.store_adapter import ConfigStoreAdapter
    from .service import VehicleClassService
    from .view import VehicleClassEditorView
    from .viewmodel import VehicleClassEditorVM

    service = VehicleClassService(store_adapter=ConfigStoreAdapter())
    viewmodel = VehicleClassEditorVM(service)
    view = VehicleClassEditorView(parent)
    view.bind_to(viewmodel)
    return view
