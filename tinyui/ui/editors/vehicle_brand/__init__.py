# editors/vehicle_brand/__init__.py


def create_vehicle_brand_editor(parent=None):
    """
    Factory for vehicle brand editor.
    Lazy imports to avoid triggering backend at import time.
    """
    from ..core.store_adapter import ConfigStoreAdapter
    from .service import VehicleBrandService
    from .view import VehicleBrandEditorView
    from .viewmodel import VehicleBrandEditorVM

    service = VehicleBrandService(store_adapter=ConfigStoreAdapter())
    viewmodel = VehicleBrandEditorVM(service)
    view = VehicleBrandEditorView(parent)
    view.bind_to(viewmodel)
    return view
