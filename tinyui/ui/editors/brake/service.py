#
#  TinyUi - Brake Editor Service
#  Copyright (C) 2026 Oost-hash
#

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from ..core.editor_service import EditorService

# Default heatmap constant - avoids import of backend at module level
HEATMAP_DEFAULT_BRAKE = "default"


@dataclass
class Brake:
    """Domain model for brake configuration."""

    name: str
    failure_thickness: float = 0.0
    heatmap: str = HEATMAP_DEFAULT_BRAKE

    def to_dict(self) -> dict:
        return {"failure_thickness": self.failure_thickness, "heatmap": self.heatmap}

    @classmethod
    def from_dict(cls, name: str, data: dict) -> "Brake":
        return cls(
            name=name,
            failure_thickness=data.get("failure_thickness", 0.0),
            heatmap=data.get("heatmap", HEATMAP_DEFAULT_BRAKE),
        )


class BrakeService(EditorService[Brake]):
    """
    Service for brake editor.
    Handles API integration, data transformation, and persistence.
    """

    def __init__(self, store_adapter: Any):
        super().__init__(store_adapter, schema=None)
        self._cfg_attr = "brakes"
        self._cfg_type = None  # Lazy loaded

    @property
    def cfg_type(self):
        if self._cfg_type is None:
            from tinyui.backend.constants import ConfigType

            self._cfg_type = ConfigType.BRAKES
        return self._cfg_type

    def load(self) -> Dict[str, Brake]:
        """Load brakes from store and convert to domain models."""
        self.load_started.emit()

        try:
            raw_data = self._store.load(self._cfg_attr)
            models = {
                name: Brake.from_dict(name, data) for name, data in raw_data.items()
            }
            self._cache = models
            self.load_completed.emit(models)
            return models

        except Exception as e:
            self.load_failed.emit(str(e))
            return {}

    def save(self, data: Dict[str, Brake]) -> bool:
        """Validate and save brake data."""
        self.save_started.emit()

        # Validate
        is_valid, error = self.validate(data)
        if not is_valid:
            self.save_failed.emit(error)
            return False

        # Transform to raw dict
        raw_data = {name: brake.to_dict() for name, brake in data.items()}

        # Persist
        try:
            self._store.save(self._cfg_attr, self.cfg_type, raw_data)
            self.save_completed.emit()
            return True

        except Exception as e:
            self.save_failed.emit(str(e))
            return False

    def validate(self, data: Dict[str, Brake]) -> tuple[bool, Optional[str]]:
        """Validate brake data."""
        for name, brake in data.items():
            if brake.failure_thickness < 0:
                return False, f"{name}: failure thickness cannot be negative"
            if not brake.heatmap:
                return False, f"{name}: heatmap required"
        return True, None

    def import_from_api(self) -> Dict[str, Brake]:
        """Import brake definitions from game API."""
        brakes = {}

        try:
            from tinyui.backend.controls import api
            from tinyui.backend.data import set_predefined_brake_name

            veh_total = api.read.vehicle.total_vehicles()

            for idx in range(veh_total):
                class_name = api.read.vehicle.class_name(idx)
                vehicle_name = api.read.vehicle.vehicle_name(idx)

                # Get brake names for front and rear
                for is_front in [True, False]:
                    brake_name = set_predefined_brake_name(
                        class_name, vehicle_name, is_front
                    )

                    if brake_name not in brakes:
                        brakes[brake_name] = Brake(
                            name=brake_name,
                            failure_thickness=0.0,
                            heatmap=HEATMAP_DEFAULT_BRAKE,
                        )

        except Exception as e:
            self.load_failed.emit(f"API import failed: {str(e)}")

        return brakes

    def create_brake(self, name: str) -> Brake:
        """Create new brake with defaults."""
        return Brake(name=name)
