# editors/vehicle_class/service.py

from dataclasses import dataclass
from typing import Any, Dict, Optional

from ..core.editor_service import EditorService


@dataclass
class VehicleClass:
    """Domain model for vehicle class configuration.

    Fields:
        class_name: The class key (e.g. "GT3")
        alias: Display alias
        color: Hex color string (e.g. "#FF0000")
        preset: Preserved field from existing config (not editable in table)
    """

    class_name: str
    alias: str = ""
    color: str = "#FFFFFF"
    preset: str = ""  # Preserved, not shown in table

    def to_dict(self) -> dict:
        result = {"alias": self.alias, "color": self.color}
        if self.preset:
            result["preset"] = self.preset
        return result

    @classmethod
    def from_dict(cls, class_name: str, data: dict) -> "VehicleClass":
        return cls(
            class_name=class_name,
            alias=data.get("alias", ""),
            color=data.get("color", "#FFFFFF"),
            preset=data.get("preset", ""),
        )


class VehicleClassService(EditorService[VehicleClass]):
    """
    Service for vehicle class editor.
    Preserves 'preset' field through load/save cycle.
    """

    def __init__(self, store_adapter: Any):
        super().__init__(store_adapter, schema=None)
        self._cfg_attr = "classes"
        self._cfg_type = None

    @property
    def cfg_type(self):
        if self._cfg_type is None:
            from tinyui.backend.constants import ConfigType
            self._cfg_type = ConfigType.CLASSES
        return self._cfg_type

    def load(self) -> Dict[str, VehicleClass]:
        self.load_started.emit()

        try:
            raw_data = self._store.load(self._cfg_attr)
            models = {
                name: VehicleClass.from_dict(name, data)
                for name, data in raw_data.items()
            }
            self._cache = models
            self.load_completed.emit(models)
            return models

        except Exception as e:
            self.load_failed.emit(str(e))
            return {}

    def save(self, data: Dict[str, VehicleClass]) -> bool:
        self.save_started.emit()

        is_valid, error = self.validate(data)
        if not is_valid:
            self.save_failed.emit(error)
            return False

        raw_data = {name: vc.to_dict() for name, vc in data.items()}

        try:
            self._store.save(self._cfg_attr, self.cfg_type, raw_data)
            self.save_completed.emit()
            return True

        except Exception as e:
            self.save_failed.emit(str(e))
            return False

    def validate(self, data: Dict[str, VehicleClass]) -> tuple[bool, Optional[str]]:
        for name, vc in data.items():
            if not vc.color:
                return False, f"{name}: color is required"
        return True, None

    def import_from_api(self) -> Dict[str, VehicleClass]:
        """Import vehicle classes from game API."""
        classes = {}

        try:
            from tinyui.backend.controls import api

            veh_total = api.read.vehicle.total_vehicles()
            for idx in range(veh_total):
                class_name = api.read.vehicle.class_name(idx)
                if class_name not in classes:
                    classes[class_name] = VehicleClass(
                        class_name=class_name,
                        alias=class_name,
                        color=self._random_color(class_name),
                    )

        except Exception as e:
            self.load_failed.emit(f"API import failed: {str(e)}")

        return classes

    def create_class(self, class_name: str) -> VehicleClass:
        """Create new class with defaults and random color."""
        return VehicleClass(
            class_name=class_name,
            alias="NAME",
            color=self._random_color(class_name),
        )

    @staticmethod
    def _random_color(seed: str) -> str:
        """Generate a deterministic random color from a seed string."""
        try:
            from tinyui.backend.formatter import random_color_class
            return random_color_class(seed)
        except ImportError:
            import hashlib
            h = hashlib.md5(seed.encode()).hexdigest()[:6]
            return f"#{h.upper()}"
