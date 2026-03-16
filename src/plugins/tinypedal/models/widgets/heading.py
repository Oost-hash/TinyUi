# Auto-generated widget
# Widget: heading

from dataclasses import dataclass, field
from typing import Any, Dict

from ..base import CellConfig, FontConfig, PositionConfig, WidgetConfig
from ..colors import OVERLAY


@dataclass
class Heading(WidgetConfig):
    name: str = "heading"

    # groups
    font: FontConfig = field(default_factory=FontConfig)
    position: PositionConfig = field(default_factory=lambda: PositionConfig(position_x=1015, position_y=455))

    # cells
    background: CellConfig = field(default_factory=lambda: CellConfig(id='background', show=False))
    center_mark: CellConfig = field(default_factory=lambda: CellConfig(id='center_mark'))
    circle: CellConfig = field(default_factory=lambda: CellConfig(id='circle', font_color=OVERLAY.font_color, bkg_color=OVERLAY.bkg_color))
    circle_background: CellConfig = field(default_factory=lambda: CellConfig(id='circle_background'))
    degree_sign: CellConfig = field(default_factory=lambda: CellConfig(id='degree_sign'))
    direction_line: CellConfig = field(default_factory=lambda: CellConfig(id='direction_line'))
    dot: CellConfig = field(default_factory=lambda: CellConfig(id='dot'))
    slip_angle: CellConfig = field(default_factory=lambda: CellConfig(id='slip_angle'))
    slip_angle_line: CellConfig = field(default_factory=lambda: CellConfig(id='slip_angle_line'))
    slip_angle_reading: CellConfig = field(default_factory=lambda: CellConfig(id='slip_angle_reading', show=False))
    yaw_angle: CellConfig = field(default_factory=lambda: CellConfig(id='yaw_angle'))
    yaw_angle_reading: CellConfig = field(default_factory=lambda: CellConfig(id='yaw_angle_reading'))
    yaw_line: CellConfig = field(default_factory=lambda: CellConfig(id='yaw_line'))

    # config
    center_mark_color: str = '#88999999'
    center_mark_length_scale: int = 1
    center_mark_style: int = 1
    center_mark_width: int = 1
    decimal_places: int = 0
    direction_line_color: str = '#CCFF2200'
    direction_line_head_scale: float = 0.9
    direction_line_tail_scale: float = 0.2
    direction_line_width: int = 3
    display_size: int = 150
    dot_color: str = '#FFFFFF'
    dot_outline_color: str = '#88000000'
    dot_outline_width: int = 1
    dot_size: int = 8
    slip_angle_line_color: str = '#CCFFFF00'
    slip_angle_line_head_scale: float = 0.7
    slip_angle_line_tail_scale: float = 0.2
    slip_angle_line_width: int = 3
    slip_angle_offset_x: float = 0.5
    slip_angle_offset_y: float = 0.8
    yaw_angle_offset_x: float = 0.5
    yaw_angle_offset_y: float = 0.7
    yaw_line_color: str = '#CC22FF00'
    yaw_line_head_scale: float = 0.9
    yaw_line_tail_scale: float = 0.2
    yaw_line_width: int = 3

    def to_flat(self) -> Dict[str, Any]:
        result = super().to_flat()
        result["name"] = self.name
        result.update(self.font.to_flat())
        result.update(self.position.to_flat())
        result.update(self.background.to_flat())
        result.update(self.center_mark.to_flat())
        result.update(self.circle.to_flat())
        result.update(self.circle_background.to_flat())
        result.update(self.degree_sign.to_flat())
        result.update(self.direction_line.to_flat())
        result.update(self.dot.to_flat())
        result.update(self.slip_angle.to_flat())
        result.update(self.slip_angle_line.to_flat())
        result.update(self.slip_angle_reading.to_flat())
        result.update(self.yaw_angle.to_flat())
        result.update(self.yaw_angle_reading.to_flat())
        result.update(self.yaw_line.to_flat())
        result["center_mark_color"] = self.center_mark_color
        result["center_mark_length_scale"] = self.center_mark_length_scale
        result["center_mark_style"] = self.center_mark_style
        result["center_mark_width"] = self.center_mark_width
        result["decimal_places"] = self.decimal_places
        result["direction_line_color"] = self.direction_line_color
        result["direction_line_head_scale"] = self.direction_line_head_scale
        result["direction_line_tail_scale"] = self.direction_line_tail_scale
        result["direction_line_width"] = self.direction_line_width
        result["display_size"] = self.display_size
        result["dot_color"] = self.dot_color
        result["dot_outline_color"] = self.dot_outline_color
        result["dot_outline_width"] = self.dot_outline_width
        result["dot_size"] = self.dot_size
        result["slip_angle_line_color"] = self.slip_angle_line_color
        result["slip_angle_line_head_scale"] = self.slip_angle_line_head_scale
        result["slip_angle_line_tail_scale"] = self.slip_angle_line_tail_scale
        result["slip_angle_line_width"] = self.slip_angle_line_width
        result["slip_angle_offset_x"] = self.slip_angle_offset_x
        result["slip_angle_offset_y"] = self.slip_angle_offset_y
        result["yaw_angle_offset_x"] = self.yaw_angle_offset_x
        result["yaw_angle_offset_y"] = self.yaw_angle_offset_y
        result["yaw_line_color"] = self.yaw_line_color
        result["yaw_line_head_scale"] = self.yaw_line_head_scale
        result["yaw_line_tail_scale"] = self.yaw_line_tail_scale
        result["yaw_line_width"] = self.yaw_line_width
        return result

    @classmethod
    def from_flat(cls, data: Dict[str, Any]) -> "Heading":
        obj = cls()
        obj.name = data.get("name", obj.name)
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.font = FontConfig.from_flat(data)
        obj.position = PositionConfig.from_flat(data)
        obj.background = CellConfig.from_flat(data, 'background')
        obj.center_mark = CellConfig.from_flat(data, 'center_mark')
        obj.circle = CellConfig.from_flat(data, 'circle')
        obj.circle_background = CellConfig.from_flat(data, 'circle_background')
        obj.degree_sign = CellConfig.from_flat(data, 'degree_sign')
        obj.direction_line = CellConfig.from_flat(data, 'direction_line')
        obj.dot = CellConfig.from_flat(data, 'dot')
        obj.slip_angle = CellConfig.from_flat(data, 'slip_angle')
        obj.slip_angle_line = CellConfig.from_flat(data, 'slip_angle_line')
        obj.slip_angle_reading = CellConfig.from_flat(data, 'slip_angle_reading')
        obj.yaw_angle = CellConfig.from_flat(data, 'yaw_angle')
        obj.yaw_angle_reading = CellConfig.from_flat(data, 'yaw_angle_reading')
        obj.yaw_line = CellConfig.from_flat(data, 'yaw_line')
        obj.center_mark_color = data.get("center_mark_color", obj.center_mark_color)
        obj.center_mark_length_scale = data.get("center_mark_length_scale", obj.center_mark_length_scale)
        obj.center_mark_style = data.get("center_mark_style", obj.center_mark_style)
        obj.center_mark_width = data.get("center_mark_width", obj.center_mark_width)
        obj.decimal_places = data.get("decimal_places", obj.decimal_places)
        obj.direction_line_color = data.get("direction_line_color", obj.direction_line_color)
        obj.direction_line_head_scale = data.get("direction_line_head_scale", obj.direction_line_head_scale)
        obj.direction_line_tail_scale = data.get("direction_line_tail_scale", obj.direction_line_tail_scale)
        obj.direction_line_width = data.get("direction_line_width", obj.direction_line_width)
        obj.display_size = data.get("display_size", obj.display_size)
        obj.dot_color = data.get("dot_color", obj.dot_color)
        obj.dot_outline_color = data.get("dot_outline_color", obj.dot_outline_color)
        obj.dot_outline_width = data.get("dot_outline_width", obj.dot_outline_width)
        obj.dot_size = data.get("dot_size", obj.dot_size)
        obj.slip_angle_line_color = data.get("slip_angle_line_color", obj.slip_angle_line_color)
        obj.slip_angle_line_head_scale = data.get("slip_angle_line_head_scale", obj.slip_angle_line_head_scale)
        obj.slip_angle_line_tail_scale = data.get("slip_angle_line_tail_scale", obj.slip_angle_line_tail_scale)
        obj.slip_angle_line_width = data.get("slip_angle_line_width", obj.slip_angle_line_width)
        obj.slip_angle_offset_x = data.get("slip_angle_offset_x", obj.slip_angle_offset_x)
        obj.slip_angle_offset_y = data.get("slip_angle_offset_y", obj.slip_angle_offset_y)
        obj.yaw_angle_offset_x = data.get("yaw_angle_offset_x", obj.yaw_angle_offset_x)
        obj.yaw_angle_offset_y = data.get("yaw_angle_offset_y", obj.yaw_angle_offset_y)
        obj.yaw_line_color = data.get("yaw_line_color", obj.yaw_line_color)
        obj.yaw_line_head_scale = data.get("yaw_line_head_scale", obj.yaw_line_head_scale)
        obj.yaw_line_tail_scale = data.get("yaw_line_tail_scale", obj.yaw_line_tail_scale)
        obj.yaw_line_width = data.get("yaw_line_width", obj.yaw_line_width)
        return obj

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["font"] = self.font.to_dict()
        result["position"] = self.position.to_dict()
        result["background"] = self.background.to_dict()
        result["center_mark"] = self.center_mark.to_dict()
        result["circle"] = self.circle.to_dict()
        result["circle_background"] = self.circle_background.to_dict()
        result["degree_sign"] = self.degree_sign.to_dict()
        result["direction_line"] = self.direction_line.to_dict()
        result["dot"] = self.dot.to_dict()
        result["slip_angle"] = self.slip_angle.to_dict()
        result["slip_angle_line"] = self.slip_angle_line.to_dict()
        result["slip_angle_reading"] = self.slip_angle_reading.to_dict()
        result["yaw_angle"] = self.yaw_angle.to_dict()
        result["yaw_angle_reading"] = self.yaw_angle_reading.to_dict()
        result["yaw_line"] = self.yaw_line.to_dict()
        result["center_mark_color"] = self.center_mark_color
        result["center_mark_length_scale"] = self.center_mark_length_scale
        result["center_mark_style"] = self.center_mark_style
        result["center_mark_width"] = self.center_mark_width
        result["decimal_places"] = self.decimal_places
        result["direction_line_color"] = self.direction_line_color
        result["direction_line_head_scale"] = self.direction_line_head_scale
        result["direction_line_tail_scale"] = self.direction_line_tail_scale
        result["direction_line_width"] = self.direction_line_width
        result["display_size"] = self.display_size
        result["dot_color"] = self.dot_color
        result["dot_outline_color"] = self.dot_outline_color
        result["dot_outline_width"] = self.dot_outline_width
        result["dot_size"] = self.dot_size
        result["slip_angle_line_color"] = self.slip_angle_line_color
        result["slip_angle_line_head_scale"] = self.slip_angle_line_head_scale
        result["slip_angle_line_tail_scale"] = self.slip_angle_line_tail_scale
        result["slip_angle_line_width"] = self.slip_angle_line_width
        result["slip_angle_offset_x"] = self.slip_angle_offset_x
        result["slip_angle_offset_y"] = self.slip_angle_offset_y
        result["yaw_angle_offset_x"] = self.yaw_angle_offset_x
        result["yaw_angle_offset_y"] = self.yaw_angle_offset_y
        result["yaw_line_color"] = self.yaw_line_color
        result["yaw_line_head_scale"] = self.yaw_line_head_scale
        result["yaw_line_tail_scale"] = self.yaw_line_tail_scale
        result["yaw_line_width"] = self.yaw_line_width
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Heading":
        obj = cls()
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.font = FontConfig.from_dict(data.get("font", {}))
        obj.position = PositionConfig.from_dict(data.get("position", {}))
        obj.background = CellConfig.from_dict(data.get("background", {}), 'background')
        obj.center_mark = CellConfig.from_dict(data.get("center_mark", {}), 'center_mark')
        obj.circle = CellConfig.from_dict(data.get("circle", {}), 'circle')
        obj.circle_background = CellConfig.from_dict(data.get("circle_background", {}), 'circle_background')
        obj.degree_sign = CellConfig.from_dict(data.get("degree_sign", {}), 'degree_sign')
        obj.direction_line = CellConfig.from_dict(data.get("direction_line", {}), 'direction_line')
        obj.dot = CellConfig.from_dict(data.get("dot", {}), 'dot')
        obj.slip_angle = CellConfig.from_dict(data.get("slip_angle", {}), 'slip_angle')
        obj.slip_angle_line = CellConfig.from_dict(data.get("slip_angle_line", {}), 'slip_angle_line')
        obj.slip_angle_reading = CellConfig.from_dict(data.get("slip_angle_reading", {}), 'slip_angle_reading')
        obj.yaw_angle = CellConfig.from_dict(data.get("yaw_angle", {}), 'yaw_angle')
        obj.yaw_angle_reading = CellConfig.from_dict(data.get("yaw_angle_reading", {}), 'yaw_angle_reading')
        obj.yaw_line = CellConfig.from_dict(data.get("yaw_line", {}), 'yaw_line')
        obj.center_mark_color = data.get("center_mark_color", obj.center_mark_color)
        obj.center_mark_length_scale = data.get("center_mark_length_scale", obj.center_mark_length_scale)
        obj.center_mark_style = data.get("center_mark_style", obj.center_mark_style)
        obj.center_mark_width = data.get("center_mark_width", obj.center_mark_width)
        obj.decimal_places = data.get("decimal_places", obj.decimal_places)
        obj.direction_line_color = data.get("direction_line_color", obj.direction_line_color)
        obj.direction_line_head_scale = data.get("direction_line_head_scale", obj.direction_line_head_scale)
        obj.direction_line_tail_scale = data.get("direction_line_tail_scale", obj.direction_line_tail_scale)
        obj.direction_line_width = data.get("direction_line_width", obj.direction_line_width)
        obj.display_size = data.get("display_size", obj.display_size)
        obj.dot_color = data.get("dot_color", obj.dot_color)
        obj.dot_outline_color = data.get("dot_outline_color", obj.dot_outline_color)
        obj.dot_outline_width = data.get("dot_outline_width", obj.dot_outline_width)
        obj.dot_size = data.get("dot_size", obj.dot_size)
        obj.slip_angle_line_color = data.get("slip_angle_line_color", obj.slip_angle_line_color)
        obj.slip_angle_line_head_scale = data.get("slip_angle_line_head_scale", obj.slip_angle_line_head_scale)
        obj.slip_angle_line_tail_scale = data.get("slip_angle_line_tail_scale", obj.slip_angle_line_tail_scale)
        obj.slip_angle_line_width = data.get("slip_angle_line_width", obj.slip_angle_line_width)
        obj.slip_angle_offset_x = data.get("slip_angle_offset_x", obj.slip_angle_offset_x)
        obj.slip_angle_offset_y = data.get("slip_angle_offset_y", obj.slip_angle_offset_y)
        obj.yaw_angle_offset_x = data.get("yaw_angle_offset_x", obj.yaw_angle_offset_x)
        obj.yaw_angle_offset_y = data.get("yaw_angle_offset_y", obj.yaw_angle_offset_y)
        obj.yaw_line_color = data.get("yaw_line_color", obj.yaw_line_color)
        obj.yaw_line_head_scale = data.get("yaw_line_head_scale", obj.yaw_line_head_scale)
        obj.yaw_line_tail_scale = data.get("yaw_line_tail_scale", obj.yaw_line_tail_scale)
        obj.yaw_line_width = data.get("yaw_line_width", obj.yaw_line_width)
        return obj
