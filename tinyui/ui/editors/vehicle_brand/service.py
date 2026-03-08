#
#  TinyUi - Vehicle Brand Editor Service
#  Copyright (C) 2026 Oost-hash
#

import asyncio
import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional

from ..core.editor_service import EditorService

logger = logging.getLogger(__name__)


@dataclass
class VehicleBrand:
    """Domain model for vehicle brand mapping.

    Maps vehicle name -> brand name.
    Note: stored as simple string value, not a dict.
    """

    vehicle_name: str
    brand: str = "Unknown"

    def to_value(self) -> str:
        """Export as raw string value for persistence."""
        return self.brand

    @classmethod
    def from_value(cls, vehicle_name: str, brand: str) -> "VehicleBrand":
        return cls(vehicle_name=vehicle_name, brand=brand)


class VehicleBrandService(EditorService[VehicleBrand]):
    """
    Service for vehicle brand editor.
    Handles persistence, API/file import, and validation.
    """

    def __init__(self, store_adapter: Any):
        super().__init__(store_adapter, schema=None)
        self._cfg_attr = "brands"
        self._cfg_type = None  # Lazy loaded

    @property
    def cfg_type(self):
        if self._cfg_type is None:
            from tinyui.backend.constants import ConfigType

            self._cfg_type = ConfigType.BRANDS
        return self._cfg_type

    def load(self) -> Dict[str, VehicleBrand]:
        """Load brands from store."""
        self.load_started.emit()

        try:
            raw_data = self._store.load(self._cfg_attr)
            models = {
                name: VehicleBrand.from_value(name, brand)
                for name, brand in raw_data.items()
            }
            self._cache = models
            self.load_completed.emit(models)
            return models

        except Exception as e:
            self.load_failed.emit(str(e))
            return {}

    def save(self, data: Dict[str, VehicleBrand]) -> bool:
        """Save brand data (as simple string values)."""
        self.save_started.emit()

        is_valid, error = self.validate(data)
        if not is_valid:
            self.save_failed.emit(error)
            return False

        # Transform to raw format: {vehicle_name: brand_string}
        raw_data = {name: brand.to_value() for name, brand in data.items()}

        try:
            self._store.save(self._cfg_attr, self.cfg_type, raw_data)
            self.save_completed.emit()
            return True

        except Exception as e:
            self.save_failed.emit(str(e))
            return False

    def validate(self, data: Dict[str, VehicleBrand]) -> tuple[bool, Optional[str]]:
        """Validate brand data."""
        for name, brand in data.items():
            if not brand.brand:
                return False, f"{name}: brand name is required"
        return True, None

    def import_from_api(self) -> Dict[str, VehicleBrand]:
        """Import vehicle brands from game API (shared memory)."""
        brands = {}

        try:
            from tinyui.backend.controls import api

            veh_total = api.read.vehicle.total_vehicles()
            for idx in range(veh_total):
                veh_name = api.read.vehicle.vehicle_name(idx)
                if veh_name not in brands:
                    brands[veh_name] = VehicleBrand(
                        vehicle_name=veh_name,
                        brand="Unknown",
                    )

        except Exception as e:
            self.load_failed.emit(f"API import failed: {str(e)}")

        return brands

    def import_from_rest_api(
        self, sim_name: str, host: str, port: int, resource: str
    ) -> Dict[str, VehicleBrand]:
        """Import vehicle brands from REST API."""
        brands = {}

        try:
            from tinyui.backend.misc import get_response, set_header_get

            header = set_header_get(resource, host)
            raw = asyncio.run(get_response(header, host, port, 3))
            vehicles = json.loads(raw)
            brands = self._parse_brand_data(vehicles)

        except Exception as e:
            logger.error("Failed importing from %s API", sim_name)
            self.load_failed.emit(
                f"Unable to import from {sim_name} API. "
                "Make sure game is running and try again."
            )

        return brands

    def import_from_file(self, filepath: str) -> Dict[str, VehicleBrand]:
        """Import brands from JSON file."""
        import os

        brands = {}

        try:
            if os.path.getsize(filepath) > 5120000:
                raise ValueError("File too large")

            with open(filepath, "r", encoding="utf-8") as f:
                vehicles = json.load(f)
                brands = self._parse_brand_data(vehicles)

        except Exception as e:
            logger.error("Failed importing %s", filepath)
            self.load_failed.emit(f"Cannot import file: {str(e)}")

        return brands

    def _parse_brand_data(self, vehicles: list) -> Dict[str, VehicleBrand]:
        """Parse brand data from API/file response."""
        if not vehicles:
            raise ValueError("Empty vehicle list")

        if vehicles[0].get("desc"):
            raw = {v["desc"]: v["manufacturer"] for v in vehicles}
        elif vehicles[0].get("name"):
            raw = {_parse_vehicle_name(v): v["manufacturer"] for v in vehicles}
        else:
            raise ValueError("Unknown vehicle data format")

        return {
            name: VehicleBrand(vehicle_name=name, brand=brand)
            for name, brand in raw.items()
        }

    def create_brand(self, vehicle_name: str) -> VehicleBrand:
        """Create new brand with defaults."""
        return VehicleBrand(vehicle_name=vehicle_name)


def _parse_vehicle_name(vehicle: dict) -> str:
    """Parse vehicle name from RF2 path."""
    path = vehicle.get("vehFile", "")
    parts = path.split("\\")

    if len(parts) >= 2:
        version_len = len(parts[-2]) + 1
    else:
        version_len = len(vehicle["name"].split(" ")[-1]) + 1

    return vehicle["name"][:-version_len]
