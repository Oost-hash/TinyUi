#
#  TinyUi - Vehicle Brand Editor ViewModel
#  Copyright (C) 2026 Oost-hash
#

from typing import Any, Dict, List

from ..core.base_viewmodel import BaseViewModel
from .service import VehicleBrand, VehicleBrandService


class VehicleBrandEditorVM(BaseViewModel[VehicleBrand]):
    """
    ViewModel for vehicle brand editor.
    Handles string-value data (vehicle_name -> brand_name).
    """

    def __init__(self, service: VehicleBrandService):
        super().__init__(service)
        self._service: VehicleBrandService = service

    def import_from_api(self):
        """Import brands from game API (shared memory)."""
        new_brands = self._service.import_from_api()
        self._merge_brands(new_brands)

    def import_from_rest_api(self, sim_name: str, host: str, port: int, resource: str):
        """Import brands from REST API."""
        new_brands = self._service.import_from_rest_api(sim_name, host, port, resource)
        self._merge_brands(new_brands)

    def import_from_file(self, filepath: str):
        """Import brands from JSON file."""
        new_brands = self._service.import_from_file(filepath)
        self._merge_brands(new_brands)

    def _merge_brands(self, new_brands: Dict[str, VehicleBrand]):
        """Merge imported brands into current model (new entries only)."""
        for name, brand in new_brands.items():
            if self._model and name not in self._model:
                self.add_item(name, brand.brand)

    def add_new_brand(self, base_name: str = "New Vehicle Name") -> str:
        """Create and add new brand with unique name."""
        counter = 1
        name = f"{base_name} {counter}"

        while self._model and name in self._model:
            counter += 1
            name = f"{base_name} {counter}"

        brand = self._service.create_brand(name)
        self.add_item(name, brand.brand)
        return name

    def update_brand(self, vehicle_name: str, brand: str):
        """Update brand value for a vehicle. Uses __setitem__ since value is a string."""
        if self._model and vehicle_name in self._model:
            self._model[vehicle_name] = brand

    def _validate(self) -> bool:
        """Validate all brands before save."""
        if not self._model:
            return True

        brands = {}
        for name, value in self._model.to_dict().items():
            if isinstance(value, VehicleBrand):
                brands[name] = value
            else:
                brands[name] = VehicleBrand.from_value(name, value)

        is_valid, error = self._service.validate(brands)

        if not is_valid:
            self.error_occurred.emit(error)

        return is_valid

    def get_row_data(self, key: str, item: Any) -> List[Any]:
        """
        Convert brand to table row.
        Returns: [vehicle_name, brand_name]
        """
        if isinstance(item, str):
            return [key, item]
        if isinstance(item, VehicleBrand):
            return [key, item.brand]
        return [key, "Unknown"]
