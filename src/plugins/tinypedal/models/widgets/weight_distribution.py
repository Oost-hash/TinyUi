# Auto-generated widget
# Widget: weight_distribution

from dataclasses import dataclass, field
from typing import Any, Dict

from ..base import CellConfig, FontConfig, PositionConfig, WidgetConfig


@dataclass
class WeightDistribution(WidgetConfig):
    name: str = "weight_distribution"

    # groups
    font: FontConfig = field(default_factory=FontConfig)
    position: PositionConfig = field(default_factory=lambda: PositionConfig(position_x=830, position_y=720))

    # cells
    cross_weight: CellConfig = field(default_factory=lambda: CellConfig(id='cross_weight', bkg_color='#8800CC', prefix='C ', column_index=3))
    front_to_rear_distribution: CellConfig = field(default_factory=lambda: CellConfig(id='front_to_rear_distribution', prefix='F ', column_index=1))
    left_to_right_distribution: CellConfig = field(default_factory=lambda: CellConfig(id='left_to_right_distribution', prefix='L ', column_index=2))
    percentage_sign: CellConfig = field(default_factory=lambda: CellConfig(id='percentage_sign'))

    # config
    decimal_places: int = 1
    smoothing_samples: int = 10

    def to_flat(self) -> Dict[str, Any]:
        result = super().to_flat()
        result["name"] = self.name
        result.update(self.font.to_flat())
        result.update(self.position.to_flat())
        result.update(self.cross_weight.to_flat())
        result.update(self.front_to_rear_distribution.to_flat())
        result.update(self.left_to_right_distribution.to_flat())
        result.update(self.percentage_sign.to_flat())
        result["decimal_places"] = self.decimal_places
        result["smoothing_samples"] = self.smoothing_samples
        return result

    @classmethod
    def from_flat(cls, data: Dict[str, Any]) -> "WeightDistribution":
        obj = cls()
        obj.name = data.get("name", obj.name)
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.font = FontConfig.from_flat(data)
        obj.position = PositionConfig.from_flat(data)
        obj.cross_weight = CellConfig.from_flat(data, 'cross_weight')
        obj.front_to_rear_distribution = CellConfig.from_flat(data, 'front_to_rear_distribution')
        obj.left_to_right_distribution = CellConfig.from_flat(data, 'left_to_right_distribution')
        obj.percentage_sign = CellConfig.from_flat(data, 'percentage_sign')
        obj.decimal_places = data.get("decimal_places", obj.decimal_places)
        obj.smoothing_samples = data.get("smoothing_samples", obj.smoothing_samples)
        return obj

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["font"] = self.font.to_dict()
        result["position"] = self.position.to_dict()
        result["cross_weight"] = self.cross_weight.to_dict()
        result["front_to_rear_distribution"] = self.front_to_rear_distribution.to_dict()
        result["left_to_right_distribution"] = self.left_to_right_distribution.to_dict()
        result["percentage_sign"] = self.percentage_sign.to_dict()
        result["decimal_places"] = self.decimal_places
        result["smoothing_samples"] = self.smoothing_samples
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WeightDistribution":
        obj = cls()
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.font = FontConfig.from_dict(data.get("font", {}))
        obj.position = PositionConfig.from_dict(data.get("position", {}))
        obj.cross_weight = CellConfig.from_dict(data.get("cross_weight", {}), 'cross_weight')
        obj.front_to_rear_distribution = CellConfig.from_dict(data.get("front_to_rear_distribution", {}), 'front_to_rear_distribution')
        obj.left_to_right_distribution = CellConfig.from_dict(data.get("left_to_right_distribution", {}), 'left_to_right_distribution')
        obj.percentage_sign = CellConfig.from_dict(data.get("percentage_sign", {}), 'percentage_sign')
        obj.decimal_places = data.get("decimal_places", obj.decimal_places)
        obj.smoothing_samples = data.get("smoothing_samples", obj.smoothing_samples)
        return obj
