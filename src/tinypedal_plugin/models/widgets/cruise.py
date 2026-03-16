# Auto-generated widget
# Widget: cruise

from dataclasses import dataclass, field
from typing import Any, Dict

from ..base import CellConfig, FontConfig, PositionConfig, WidgetConfig


@dataclass
class Cruise(WidgetConfig):
    name: str = "cruise"

    # base overrides
    layout: int = 1
    update_interval: int = 100

    # groups
    font: FontConfig = field(default_factory=FontConfig)
    position: PositionConfig = field(default_factory=lambda: PositionConfig(position_x=57, position_y=98))

    # cells
    compass: CellConfig = field(default_factory=lambda: CellConfig(id='compass', column_index=1))
    cornering_radius: CellConfig = field(default_factory=lambda: CellConfig(id='cornering_radius', column_index=5))
    distance_into_lap: CellConfig = field(default_factory=lambda: CellConfig(id='distance_into_lap', column_index=4))
    elevation: CellConfig = field(default_factory=lambda: CellConfig(id='elevation', column_index=2))
    odometer: CellConfig = field(default_factory=lambda: CellConfig(id='odometer', column_index=3))

    # config
    odometer_maximum_digits: int = 8

    def to_flat(self) -> Dict[str, Any]:
        result = super().to_flat()
        result["name"] = self.name
        result["layout"] = self.layout
        result["update_interval"] = self.update_interval
        result.update(self.font.to_flat())
        result.update(self.position.to_flat())
        result.update(self.compass.to_flat())
        result.update(self.cornering_radius.to_flat())
        result.update(self.distance_into_lap.to_flat())
        result.update(self.elevation.to_flat())
        result.update(self.odometer.to_flat())
        result["odometer_maximum_digits"] = self.odometer_maximum_digits
        return result

    @classmethod
    def from_flat(cls, data: Dict[str, Any]) -> "Cruise":
        obj = cls()
        obj.name = data.get("name", obj.name)
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.layout = data.get("layout", obj.layout)
        obj.update_interval = data.get("update_interval", obj.update_interval)
        obj.font = FontConfig.from_flat(data)
        obj.position = PositionConfig.from_flat(data)
        obj.compass = CellConfig.from_flat(data, 'compass')
        obj.cornering_radius = CellConfig.from_flat(data, 'cornering_radius')
        obj.distance_into_lap = CellConfig.from_flat(data, 'distance_into_lap')
        obj.elevation = CellConfig.from_flat(data, 'elevation')
        obj.odometer = CellConfig.from_flat(data, 'odometer')
        obj.odometer_maximum_digits = data.get("odometer_maximum_digits", obj.odometer_maximum_digits)
        return obj

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["layout"] = self.layout
        result["update_interval"] = self.update_interval
        result["font"] = self.font.to_dict()
        result["position"] = self.position.to_dict()
        result["compass"] = self.compass.to_dict()
        result["cornering_radius"] = self.cornering_radius.to_dict()
        result["distance_into_lap"] = self.distance_into_lap.to_dict()
        result["elevation"] = self.elevation.to_dict()
        result["odometer"] = self.odometer.to_dict()
        result["odometer_maximum_digits"] = self.odometer_maximum_digits
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Cruise":
        obj = cls()
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.layout = data.get("layout", obj.layout)
        obj.update_interval = data.get("update_interval", obj.update_interval)
        obj.font = FontConfig.from_dict(data.get("font", {}))
        obj.position = PositionConfig.from_dict(data.get("position", {}))
        obj.compass = CellConfig.from_dict(data.get("compass", {}), 'compass')
        obj.cornering_radius = CellConfig.from_dict(data.get("cornering_radius", {}), 'cornering_radius')
        obj.distance_into_lap = CellConfig.from_dict(data.get("distance_into_lap", {}), 'distance_into_lap')
        obj.elevation = CellConfig.from_dict(data.get("elevation", {}), 'elevation')
        obj.odometer = CellConfig.from_dict(data.get("odometer", {}), 'odometer')
        obj.odometer_maximum_digits = data.get("odometer_maximum_digits", obj.odometer_maximum_digits)
        return obj
