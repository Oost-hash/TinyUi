# editors/brake/viewmodel.py

from typing import Any, List

from ..core.base_viewmodel import BaseViewModel
from .service import Brake, BrakeService


class BrakeEditorVM(BaseViewModel[Brake]):
    """
    ViewModel for brake editor.
    Exposes brake-specific operations to the View.
    """

    def __init__(self, service: BrakeService):
        super().__init__(service)
        self._service: BrakeService = service

    def import_from_api(self):
        """Import brakes from game API and add to model."""
        new_brakes = self._service.import_from_api()

        for name, brake in new_brakes.items():
            if self._model and name not in self._model:
                self.add_item(name, brake.to_dict())

    def add_new_brake(self, base_name: str = "New Brake") -> str:
        """Create and add new brake with unique name."""
        # Generate unique name
        counter = 1
        name = f"{base_name} {counter}"

        while self._model and name in self._model:
            counter += 1
            name = f"{base_name} {counter}"

        brake = self._service.create_brake(name)
        self.add_item(name, brake.to_dict())
        return name

    def update_brake_field(self, brake_name: str, field: str, value: Any):
        """Update a single field of a brake."""
        self.update_value(brake_name, field, value)

    def _validate(self) -> bool:
        """Validate all brakes before save."""
        if not self._model:
            return True

        brakes = {}
        for name, data in self._model.to_dict().items():
            if isinstance(data, Brake):
                brakes[name] = data
            else:
                brakes[name] = Brake.from_dict(name, data)

        is_valid, error = self._service.validate(brakes)

        if not is_valid:
            self.error_occurred.emit(error)

        return is_valid

    def get_row_data(self, key: str, item: Any) -> List[Any]:
        """
        Convert brake data to table row format.
        Returns: [name, failure_thickness, heatmap]
        """
        if isinstance(item, dict):
            return [
                key,
                item.get("failure_thickness", 0.0),
                item.get("heatmap", "default"),
            ]
        return [key, "", ""]

    @property
    def heatmap_options(self) -> List[str]:
        """Get available heatmap names for dropdown."""
        # This would come from a heatmap service in real implementation
        from tinyui.backend.settings import cfg

        return (
            list(cfg.user.heatmap.keys())
            if hasattr(cfg.user, "heatmap")
            else ["default"]
        )
