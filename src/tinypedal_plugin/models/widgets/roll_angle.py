# Auto-generated widget
# Widget: roll_angle

from dataclasses import dataclass, field
from typing import Any, Dict

from ..base import CellConfig, FontConfig, PositionConfig, WidgetConfig
from ..colors import PLAYER, PLAYER_HIGHLIGHT


@dataclass
class RollAngle(WidgetConfig):
    name: str = "roll_angle"

    # groups
    font: FontConfig = field(default_factory=FontConfig)
    position: PositionConfig = field(default_factory=lambda: PositionConfig(position_x=770, position_y=720))

    # cells
    degree_and_percentage_sign: CellConfig = field(default_factory=lambda: CellConfig(id='degree_and_percentage_sign'))
    roll_angle_difference: CellConfig = field(default_factory=lambda: CellConfig(id='roll_angle_difference', bkg_color='#0066CC', column_index=3))
    roll_angle_front: CellConfig = field(default_factory=lambda: CellConfig(id='roll_angle_front', column_index=1))
    roll_angle_ratio: CellConfig = field(default_factory=lambda: CellConfig(id='roll_angle_ratio', font_color=PLAYER_HIGHLIGHT.font_color, bkg_color=PLAYER_HIGHLIGHT.bkg_color, column_index=4))
    roll_angle_rear: CellConfig = field(default_factory=lambda: CellConfig(id='roll_angle_rear', column_index=2))

    # config
    decimal_places: int = 2
    roll_angle_ratio_smoothing_samples: int = 50
    roll_angle_smoothing_samples: int = 10
    wheel_track_front: int = 2000
    wheel_track_rear: int = 2000

    def to_flat(self) -> Dict[str, Any]:
        result = super().to_flat()
        result["name"] = self.name
        result.update(self.font.to_flat())
        result.update(self.position.to_flat())
        result.update(self.degree_and_percentage_sign.to_flat())
        result.update(self.roll_angle_difference.to_flat())
        result.update(self.roll_angle_front.to_flat())
        result.update(self.roll_angle_ratio.to_flat())
        result.update(self.roll_angle_rear.to_flat())
        result["decimal_places"] = self.decimal_places
        result["roll_angle_ratio_smoothing_samples"] = self.roll_angle_ratio_smoothing_samples
        result["roll_angle_smoothing_samples"] = self.roll_angle_smoothing_samples
        result["wheel_track_front"] = self.wheel_track_front
        result["wheel_track_rear"] = self.wheel_track_rear
        return result

    @classmethod
    def from_flat(cls, data: Dict[str, Any]) -> "RollAngle":
        obj = cls()
        obj.name = data.get("name", obj.name)
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.font = FontConfig.from_flat(data)
        obj.position = PositionConfig.from_flat(data)
        obj.degree_and_percentage_sign = CellConfig.from_flat(data, 'degree_and_percentage_sign')
        obj.roll_angle_difference = CellConfig.from_flat(data, 'roll_angle_difference')
        obj.roll_angle_front = CellConfig.from_flat(data, 'roll_angle_front')
        obj.roll_angle_ratio = CellConfig.from_flat(data, 'roll_angle_ratio')
        obj.roll_angle_rear = CellConfig.from_flat(data, 'roll_angle_rear')
        obj.decimal_places = data.get("decimal_places", obj.decimal_places)
        obj.roll_angle_ratio_smoothing_samples = data.get("roll_angle_ratio_smoothing_samples", obj.roll_angle_ratio_smoothing_samples)
        obj.roll_angle_smoothing_samples = data.get("roll_angle_smoothing_samples", obj.roll_angle_smoothing_samples)
        obj.wheel_track_front = data.get("wheel_track_front", obj.wheel_track_front)
        obj.wheel_track_rear = data.get("wheel_track_rear", obj.wheel_track_rear)
        return obj

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["font"] = self.font.to_dict()
        result["position"] = self.position.to_dict()
        result["degree_and_percentage_sign"] = self.degree_and_percentage_sign.to_dict()
        result["roll_angle_difference"] = self.roll_angle_difference.to_dict()
        result["roll_angle_front"] = self.roll_angle_front.to_dict()
        result["roll_angle_ratio"] = self.roll_angle_ratio.to_dict()
        result["roll_angle_rear"] = self.roll_angle_rear.to_dict()
        result["decimal_places"] = self.decimal_places
        result["roll_angle_ratio_smoothing_samples"] = self.roll_angle_ratio_smoothing_samples
        result["roll_angle_smoothing_samples"] = self.roll_angle_smoothing_samples
        result["wheel_track_front"] = self.wheel_track_front
        result["wheel_track_rear"] = self.wheel_track_rear
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RollAngle":
        obj = cls()
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.font = FontConfig.from_dict(data.get("font", {}))
        obj.position = PositionConfig.from_dict(data.get("position", {}))
        obj.degree_and_percentage_sign = CellConfig.from_dict(data.get("degree_and_percentage_sign", {}), 'degree_and_percentage_sign')
        obj.roll_angle_difference = CellConfig.from_dict(data.get("roll_angle_difference", {}), 'roll_angle_difference')
        obj.roll_angle_front = CellConfig.from_dict(data.get("roll_angle_front", {}), 'roll_angle_front')
        obj.roll_angle_ratio = CellConfig.from_dict(data.get("roll_angle_ratio", {}), 'roll_angle_ratio')
        obj.roll_angle_rear = CellConfig.from_dict(data.get("roll_angle_rear", {}), 'roll_angle_rear')
        obj.decimal_places = data.get("decimal_places", obj.decimal_places)
        obj.roll_angle_ratio_smoothing_samples = data.get("roll_angle_ratio_smoothing_samples", obj.roll_angle_ratio_smoothing_samples)
        obj.roll_angle_smoothing_samples = data.get("roll_angle_smoothing_samples", obj.roll_angle_smoothing_samples)
        obj.wheel_track_front = data.get("wheel_track_front", obj.wheel_track_front)
        obj.wheel_track_rear = data.get("wheel_track_rear", obj.wheel_track_rear)
        return obj
