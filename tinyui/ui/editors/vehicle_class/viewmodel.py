# editors/vehicle_class/viewmodel.py

from typing import Any, List

from ..core.base_viewmodel import BaseViewModel
from .service import VehicleClass, VehicleClassService


class VehicleClassEditorVM(BaseViewModel[VehicleClass]):
    """ViewModel for vehicle class editor."""

    def __init__(self, service: VehicleClassService):
        super().__init__(service)
        self._service: VehicleClassService = service

    def import_from_api(self):
        """Import classes from game API."""
        new_classes = self._service.import_from_api()

        for name, vc in new_classes.items():
            if self._model and name not in self._model:
                self.add_item(name, vc.to_dict())

    def add_new_class(self, base_name: str = "New Class Name") -> str:
        """Create and add new class with unique name."""
        counter = 1
        name = f"{base_name} {counter}"

        while self._model and name in self._model:
            counter += 1
            name = f"{base_name} {counter}"

        vc = self._service.create_class(name)
        self.add_item(name, vc.to_dict())
        return name

    def update_class_field(self, class_name: str, field: str, value: Any):
        """Update a single field of a class."""
        self.update_value(class_name, field, value)

    def _validate(self) -> bool:
        if not self._model:
            return True

        classes = {}
        for name, data in self._model.to_dict().items():
            if isinstance(data, VehicleClass):
                classes[name] = data
            else:
                classes[name] = VehicleClass.from_dict(name, data)

        is_valid, error = self._service.validate(classes)

        if not is_valid:
            self.error_occurred.emit(error)

        return is_valid

    def get_row_data(self, key: str, item: Any) -> List[Any]:
        """
        Convert class to table row.
        Returns: [class_name, alias, color]
        """
        if isinstance(item, dict):
            return [key, item.get("alias", ""), item.get("color", "#FFFFFF")]
        if isinstance(item, VehicleClass):
            return [key, item.alias, item.color]
        return [key, "", "#FFFFFF"]
