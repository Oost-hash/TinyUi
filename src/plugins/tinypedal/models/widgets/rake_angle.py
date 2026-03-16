# Auto-generated widget
# Widget: rake_angle

from dataclasses import dataclass, field
from typing import Any, Dict

from ..base import CellConfig, FontConfig, PositionConfig, WidgetConfig


@dataclass
class RakeAngle(WidgetConfig):
    name: str = "rake_angle"

    # groups
    font: FontConfig = field(default_factory=FontConfig)
    position: PositionConfig = field(default_factory=lambda: PositionConfig(position_x=593, position_y=315))

    # cells
    degree_sign: CellConfig = field(default_factory=lambda: CellConfig(id='degree_sign'))
    rake_angle: CellConfig = field(default_factory=lambda: CellConfig(id='rake_angle', prefix='RA '))
    ride_height_difference: CellConfig = field(default_factory=lambda: CellConfig(id='ride_height_difference'))

    # config
    decimal_places: int = 2
    rake_angle_smoothing_samples: int = 10
    warning_color_negative_rake: str = '#00AAFF'
    wheelbase: int = 2800

    def to_flat(self) -> Dict[str, Any]:
        result = super().to_flat()
        result["name"] = self.name
        result.update(self.font.to_flat())
        result.update(self.position.to_flat())
        result.update(self.degree_sign.to_flat())
        result.update(self.rake_angle.to_flat())
        result.update(self.ride_height_difference.to_flat())
        result["decimal_places"] = self.decimal_places
        result["rake_angle_smoothing_samples"] = self.rake_angle_smoothing_samples
        result["warning_color_negative_rake"] = self.warning_color_negative_rake
        result["wheelbase"] = self.wheelbase
        return result

    @classmethod
    def from_flat(cls, data: Dict[str, Any]) -> "RakeAngle":
        obj = cls()
        obj.name = data.get("name", obj.name)
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.font = FontConfig.from_flat(data)
        obj.position = PositionConfig.from_flat(data)
        obj.degree_sign = CellConfig.from_flat(data, 'degree_sign')
        obj.rake_angle = CellConfig.from_flat(data, 'rake_angle')
        obj.ride_height_difference = CellConfig.from_flat(data, 'ride_height_difference')
        obj.decimal_places = data.get("decimal_places", obj.decimal_places)
        obj.rake_angle_smoothing_samples = data.get("rake_angle_smoothing_samples", obj.rake_angle_smoothing_samples)
        obj.warning_color_negative_rake = data.get("warning_color_negative_rake", obj.warning_color_negative_rake)
        obj.wheelbase = data.get("wheelbase", obj.wheelbase)
        return obj

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["font"] = self.font.to_dict()
        result["position"] = self.position.to_dict()
        result["degree_sign"] = self.degree_sign.to_dict()
        result["rake_angle"] = self.rake_angle.to_dict()
        result["ride_height_difference"] = self.ride_height_difference.to_dict()
        result["decimal_places"] = self.decimal_places
        result["rake_angle_smoothing_samples"] = self.rake_angle_smoothing_samples
        result["warning_color_negative_rake"] = self.warning_color_negative_rake
        result["wheelbase"] = self.wheelbase
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RakeAngle":
        obj = cls()
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.font = FontConfig.from_dict(data.get("font", {}))
        obj.position = PositionConfig.from_dict(data.get("position", {}))
        obj.degree_sign = CellConfig.from_dict(data.get("degree_sign", {}), 'degree_sign')
        obj.rake_angle = CellConfig.from_dict(data.get("rake_angle", {}), 'rake_angle')
        obj.ride_height_difference = CellConfig.from_dict(data.get("ride_height_difference", {}), 'ride_height_difference')
        obj.decimal_places = data.get("decimal_places", obj.decimal_places)
        obj.rake_angle_smoothing_samples = data.get("rake_angle_smoothing_samples", obj.rake_angle_smoothing_samples)
        obj.warning_color_negative_rake = data.get("warning_color_negative_rake", obj.warning_color_negative_rake)
        obj.wheelbase = data.get("wheelbase", obj.wheelbase)
        return obj
