# Auto-generated widget
# Widget: steering_wheel

from dataclasses import dataclass, field
from typing import Any, Dict

from ..base import CellConfig, FontConfig, PositionConfig, WidgetConfig


@dataclass
class SteeringWheel(WidgetConfig):
    name: str = "steering_wheel"

    # base overrides
    bkg_color: str = '#88111111'

    # groups
    font: FontConfig = field(default_factory=FontConfig)
    position: PositionConfig = field(default_factory=lambda: PositionConfig(position_x=1050, position_y=620))

    # cells
    background: CellConfig = field(default_factory=lambda: CellConfig(id='background', show=False))
    circle: CellConfig = field(default_factory=lambda: CellConfig(id='circle', bkg_color='#88111111'))
    circle_background: CellConfig = field(default_factory=lambda: CellConfig(id='circle_background'))
    custom_steering_wheel: CellConfig = field(default_factory=lambda: CellConfig(id='custom_steering_wheel', show=False))
    degree_sign: CellConfig = field(default_factory=lambda: CellConfig(id='degree_sign'))
    rotation_line: CellConfig = field(default_factory=lambda: CellConfig(id='rotation_line'))
    rotation_line_while_stationary_only: CellConfig = field(default_factory=lambda: CellConfig(id='rotation_line_while_stationary_only'))
    steering_angle: CellConfig = field(default_factory=lambda: CellConfig(id='steering_angle', show=False))

    # config
    custom_steering_wheel_image_file: str = ''
    decimal_places: int = 0
    display_margin: int = 4
    display_size: int = 80
    manual_steering_range: int = 0
    rotation_line_color: str = '#DD2200'
    rotation_line_margin: int = 2
    rotation_line_width: int = 3
    steering_angle_offset_x: float = 0.5
    steering_angle_offset_y: float = 0.5

    def to_flat(self) -> Dict[str, Any]:
        result = super().to_flat()
        result["name"] = self.name
        result["bkg_color"] = self.bkg_color
        result.update(self.font.to_flat())
        result.update(self.position.to_flat())
        result.update(self.background.to_flat())
        result.update(self.circle.to_flat())
        result.update(self.circle_background.to_flat())
        result.update(self.custom_steering_wheel.to_flat())
        result.update(self.degree_sign.to_flat())
        result.update(self.rotation_line.to_flat())
        result.update(self.rotation_line_while_stationary_only.to_flat())
        result.update(self.steering_angle.to_flat())
        result["custom_steering_wheel_image_file"] = self.custom_steering_wheel_image_file
        result["decimal_places"] = self.decimal_places
        result["display_margin"] = self.display_margin
        result["display_size"] = self.display_size
        result["manual_steering_range"] = self.manual_steering_range
        result["rotation_line_color"] = self.rotation_line_color
        result["rotation_line_margin"] = self.rotation_line_margin
        result["rotation_line_width"] = self.rotation_line_width
        result["steering_angle_offset_x"] = self.steering_angle_offset_x
        result["steering_angle_offset_y"] = self.steering_angle_offset_y
        return result

    @classmethod
    def from_flat(cls, data: Dict[str, Any]) -> "SteeringWheel":
        obj = cls()
        obj.name = data.get("name", obj.name)
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.bkg_color = data.get("bkg_color", obj.bkg_color)
        obj.font = FontConfig.from_flat(data)
        obj.position = PositionConfig.from_flat(data)
        obj.background = CellConfig.from_flat(data, 'background')
        obj.circle = CellConfig.from_flat(data, 'circle')
        obj.circle_background = CellConfig.from_flat(data, 'circle_background')
        obj.custom_steering_wheel = CellConfig.from_flat(data, 'custom_steering_wheel')
        obj.degree_sign = CellConfig.from_flat(data, 'degree_sign')
        obj.rotation_line = CellConfig.from_flat(data, 'rotation_line')
        obj.rotation_line_while_stationary_only = CellConfig.from_flat(data, 'rotation_line_while_stationary_only')
        obj.steering_angle = CellConfig.from_flat(data, 'steering_angle')
        obj.custom_steering_wheel_image_file = data.get("custom_steering_wheel_image_file", obj.custom_steering_wheel_image_file)
        obj.decimal_places = data.get("decimal_places", obj.decimal_places)
        obj.display_margin = data.get("display_margin", obj.display_margin)
        obj.display_size = data.get("display_size", obj.display_size)
        obj.manual_steering_range = data.get("manual_steering_range", obj.manual_steering_range)
        obj.rotation_line_color = data.get("rotation_line_color", obj.rotation_line_color)
        obj.rotation_line_margin = data.get("rotation_line_margin", obj.rotation_line_margin)
        obj.rotation_line_width = data.get("rotation_line_width", obj.rotation_line_width)
        obj.steering_angle_offset_x = data.get("steering_angle_offset_x", obj.steering_angle_offset_x)
        obj.steering_angle_offset_y = data.get("steering_angle_offset_y", obj.steering_angle_offset_y)
        return obj

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["bkg_color"] = self.bkg_color
        result["font"] = self.font.to_dict()
        result["position"] = self.position.to_dict()
        result["background"] = self.background.to_dict()
        result["circle"] = self.circle.to_dict()
        result["circle_background"] = self.circle_background.to_dict()
        result["custom_steering_wheel"] = self.custom_steering_wheel.to_dict()
        result["degree_sign"] = self.degree_sign.to_dict()
        result["rotation_line"] = self.rotation_line.to_dict()
        result["rotation_line_while_stationary_only"] = self.rotation_line_while_stationary_only.to_dict()
        result["steering_angle"] = self.steering_angle.to_dict()
        result["custom_steering_wheel_image_file"] = self.custom_steering_wheel_image_file
        result["decimal_places"] = self.decimal_places
        result["display_margin"] = self.display_margin
        result["display_size"] = self.display_size
        result["manual_steering_range"] = self.manual_steering_range
        result["rotation_line_color"] = self.rotation_line_color
        result["rotation_line_margin"] = self.rotation_line_margin
        result["rotation_line_width"] = self.rotation_line_width
        result["steering_angle_offset_x"] = self.steering_angle_offset_x
        result["steering_angle_offset_y"] = self.steering_angle_offset_y
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SteeringWheel":
        obj = cls()
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.bkg_color = data.get("bkg_color", obj.bkg_color)
        obj.font = FontConfig.from_dict(data.get("font", {}))
        obj.position = PositionConfig.from_dict(data.get("position", {}))
        obj.background = CellConfig.from_dict(data.get("background", {}), 'background')
        obj.circle = CellConfig.from_dict(data.get("circle", {}), 'circle')
        obj.circle_background = CellConfig.from_dict(data.get("circle_background", {}), 'circle_background')
        obj.custom_steering_wheel = CellConfig.from_dict(data.get("custom_steering_wheel", {}), 'custom_steering_wheel')
        obj.degree_sign = CellConfig.from_dict(data.get("degree_sign", {}), 'degree_sign')
        obj.rotation_line = CellConfig.from_dict(data.get("rotation_line", {}), 'rotation_line')
        obj.rotation_line_while_stationary_only = CellConfig.from_dict(data.get("rotation_line_while_stationary_only", {}), 'rotation_line_while_stationary_only')
        obj.steering_angle = CellConfig.from_dict(data.get("steering_angle", {}), 'steering_angle')
        obj.custom_steering_wheel_image_file = data.get("custom_steering_wheel_image_file", obj.custom_steering_wheel_image_file)
        obj.decimal_places = data.get("decimal_places", obj.decimal_places)
        obj.display_margin = data.get("display_margin", obj.display_margin)
        obj.display_size = data.get("display_size", obj.display_size)
        obj.manual_steering_range = data.get("manual_steering_range", obj.manual_steering_range)
        obj.rotation_line_color = data.get("rotation_line_color", obj.rotation_line_color)
        obj.rotation_line_margin = data.get("rotation_line_margin", obj.rotation_line_margin)
        obj.rotation_line_width = data.get("rotation_line_width", obj.rotation_line_width)
        obj.steering_angle_offset_x = data.get("steering_angle_offset_x", obj.steering_angle_offset_x)
        obj.steering_angle_offset_y = data.get("steering_angle_offset_y", obj.steering_angle_offset_y)
        return obj
