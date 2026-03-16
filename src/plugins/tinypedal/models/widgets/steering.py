# Auto-generated widget
# Widget: steering

from dataclasses import dataclass, field
from typing import Any, Dict

from ..base import BarConfig, CellConfig, FontConfig, PositionConfig, WidgetConfig


@dataclass
class Steering(WidgetConfig):
    name: str = "steering"

    # groups
    bar: BarConfig = field(default_factory=BarConfig)
    font: FontConfig = field(default_factory=FontConfig)
    position: PositionConfig = field(default_factory=lambda: PositionConfig(position_x=585, position_y=358))

    # cells
    scale_mark: CellConfig = field(default_factory=lambda: CellConfig(id='scale_mark'))
    steering_angle: CellConfig = field(default_factory=lambda: CellConfig(id='steering_angle'))

    # config
    bar_edge_color: str = '#FFAA00'
    bar_edge_width: int = 2
    bar_height: int = 15
    font_color: str = '#AAAAAA'
    manual_steering_range: int = 0
    scale_mark_color: str = '#555555'
    scale_mark_degree: int = 90
    steering_color: str = '#FFAA00'

    def to_flat(self) -> Dict[str, Any]:
        result = super().to_flat()
        result["name"] = self.name
        result.update(self.bar.to_flat())
        result.update(self.font.to_flat())
        result.update(self.position.to_flat())
        result.update(self.scale_mark.to_flat())
        result.update(self.steering_angle.to_flat())
        result["bar_edge_color"] = self.bar_edge_color
        result["bar_edge_width"] = self.bar_edge_width
        result["bar_height"] = self.bar_height
        result["font_color"] = self.font_color
        result["manual_steering_range"] = self.manual_steering_range
        result["scale_mark_color"] = self.scale_mark_color
        result["scale_mark_degree"] = self.scale_mark_degree
        result["steering_color"] = self.steering_color
        return result

    @classmethod
    def from_flat(cls, data: Dict[str, Any]) -> "Steering":
        obj = cls()
        obj.name = data.get("name", obj.name)
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.bar = BarConfig.from_flat(data)
        obj.font = FontConfig.from_flat(data)
        obj.position = PositionConfig.from_flat(data)
        obj.scale_mark = CellConfig.from_flat(data, 'scale_mark')
        obj.steering_angle = CellConfig.from_flat(data, 'steering_angle')
        obj.bar_edge_color = data.get("bar_edge_color", obj.bar_edge_color)
        obj.bar_edge_width = data.get("bar_edge_width", obj.bar_edge_width)
        obj.bar_height = data.get("bar_height", obj.bar_height)
        obj.font_color = data.get("font_color", obj.font_color)
        obj.manual_steering_range = data.get("manual_steering_range", obj.manual_steering_range)
        obj.scale_mark_color = data.get("scale_mark_color", obj.scale_mark_color)
        obj.scale_mark_degree = data.get("scale_mark_degree", obj.scale_mark_degree)
        obj.steering_color = data.get("steering_color", obj.steering_color)
        return obj

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["bar"] = self.bar.to_dict()
        result["font"] = self.font.to_dict()
        result["position"] = self.position.to_dict()
        result["scale_mark"] = self.scale_mark.to_dict()
        result["steering_angle"] = self.steering_angle.to_dict()
        result["bar_edge_color"] = self.bar_edge_color
        result["bar_edge_width"] = self.bar_edge_width
        result["bar_height"] = self.bar_height
        result["font_color"] = self.font_color
        result["manual_steering_range"] = self.manual_steering_range
        result["scale_mark_color"] = self.scale_mark_color
        result["scale_mark_degree"] = self.scale_mark_degree
        result["steering_color"] = self.steering_color
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Steering":
        obj = cls()
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.bar = BarConfig.from_dict(data.get("bar", {}))
        obj.font = FontConfig.from_dict(data.get("font", {}))
        obj.position = PositionConfig.from_dict(data.get("position", {}))
        obj.scale_mark = CellConfig.from_dict(data.get("scale_mark", {}), 'scale_mark')
        obj.steering_angle = CellConfig.from_dict(data.get("steering_angle", {}), 'steering_angle')
        obj.bar_edge_color = data.get("bar_edge_color", obj.bar_edge_color)
        obj.bar_edge_width = data.get("bar_edge_width", obj.bar_edge_width)
        obj.bar_height = data.get("bar_height", obj.bar_height)
        obj.font_color = data.get("font_color", obj.font_color)
        obj.manual_steering_range = data.get("manual_steering_range", obj.manual_steering_range)
        obj.scale_mark_color = data.get("scale_mark_color", obj.scale_mark_color)
        obj.scale_mark_degree = data.get("scale_mark_degree", obj.scale_mark_degree)
        obj.steering_color = data.get("steering_color", obj.steering_color)
        return obj
