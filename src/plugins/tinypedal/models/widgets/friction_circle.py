# Auto-generated widget
# Widget: friction_circle

from dataclasses import dataclass, field
from typing import Any, Dict

from ..base import CellConfig, FontConfig, PositionConfig, WidgetConfig
from ..colors import OVERLAY


@dataclass
class FrictionCircle(WidgetConfig):
    name: str = "friction_circle"

    # groups
    font: FontConfig = field(default_factory=lambda: FontConfig(font_size=13))
    position: PositionConfig = field(default_factory=lambda: PositionConfig(position_x=1000, position_y=266))

    # cells
    background: CellConfig = field(default_factory=lambda: CellConfig(id='background', show=False))
    center_mark: CellConfig = field(default_factory=lambda: CellConfig(id='center_mark'))
    circle: CellConfig = field(default_factory=lambda: CellConfig(id='circle', font_color=OVERLAY.font_color, bkg_color=OVERLAY.bkg_color))
    circle_background: CellConfig = field(default_factory=lambda: CellConfig(id='circle_background', show=False))
    dot: CellConfig = field(default_factory=lambda: CellConfig(id='dot'))
    fade_out: CellConfig = field(default_factory=lambda: CellConfig(id='fade_out'))
    highlight: CellConfig = field(default_factory=lambda: CellConfig(id='highlight', font_color='#FF8800'))
    inverted_orientation: CellConfig = field(default_factory=lambda: CellConfig(id='inverted_orientation', show=False))
    max_average_lateral_g_circle: CellConfig = field(default_factory=lambda: CellConfig(id='max_average_lateral_g_circle'))
    readings: CellConfig = field(default_factory=lambda: CellConfig(id='readings'))
    trace: CellConfig = field(default_factory=lambda: CellConfig(id='trace'))
    trace_fade_out: CellConfig = field(default_factory=lambda: CellConfig(id='trace_fade_out'))

    # components
    reference_circle: dict = field(default_factory=lambda: {
    1: {'color': '#88999999', 'radius_g': 1, 'style': 1, 'width': 1},
    2: {'color': '#88999999', 'radius_g': 2, 'style': 1, 'width': 1},
    3: {'color': '#88999999', 'radius_g': 3, 'style': 1, 'width': 1},
    4: {'color': '#88999999', 'radius_g': 4, 'style': 1, 'width': 1},
    5: {'color': '#88999999', 'radius_g': 5, 'style': 1, 'width': 1},
})

    # config
    center_mark_color: str = '#88999999'
    center_mark_radius_g: int = 6
    center_mark_style: int = 1
    center_mark_width: int = 1
    display_radius_g: float = 3.2
    display_size: int = 150
    dot_color: str = '#FFFFFF'
    dot_outline_color: str = '#88000000'
    dot_outline_width: int = 1
    dot_size: int = 12
    fade_in_radius: float = 0.5
    fade_out_radius: float = 0.98
    font_color: str = '#FFFFFF'
    max_average_lateral_g_circle_color: str = '#BBFFFFFF'
    max_average_lateral_g_circle_style: int = 1
    max_average_lateral_g_circle_width: int = 3
    trace_color: str = '#CCFF2200'
    trace_fade_out_step: float = 0.2
    trace_max_samples: int = 200
    trace_style: int = 0
    trace_width: int = 3

    def to_flat(self) -> Dict[str, Any]:
        result = super().to_flat()
        result["name"] = self.name
        result.update(self.font.to_flat())
        result.update(self.position.to_flat())
        result.update(self.background.to_flat())
        result.update(self.center_mark.to_flat())
        result.update(self.circle.to_flat())
        result.update(self.circle_background.to_flat())
        result.update(self.dot.to_flat())
        result.update(self.fade_out.to_flat())
        result.update(self.highlight.to_flat())
        result.update(self.inverted_orientation.to_flat())
        result.update(self.max_average_lateral_g_circle.to_flat())
        result.update(self.readings.to_flat())
        result.update(self.trace.to_flat())
        result.update(self.trace_fade_out.to_flat())
        result["reference_circle_1_color"] = self.reference_circle[1]["color"]
        result["reference_circle_1_radius_g"] = self.reference_circle[1]["radius_g"]
        result["reference_circle_1_style"] = self.reference_circle[1]["style"]
        result["reference_circle_1_width"] = self.reference_circle[1]["width"]
        result["reference_circle_2_color"] = self.reference_circle[2]["color"]
        result["reference_circle_2_radius_g"] = self.reference_circle[2]["radius_g"]
        result["reference_circle_2_style"] = self.reference_circle[2]["style"]
        result["reference_circle_2_width"] = self.reference_circle[2]["width"]
        result["reference_circle_3_color"] = self.reference_circle[3]["color"]
        result["reference_circle_3_radius_g"] = self.reference_circle[3]["radius_g"]
        result["reference_circle_3_style"] = self.reference_circle[3]["style"]
        result["reference_circle_3_width"] = self.reference_circle[3]["width"]
        result["reference_circle_4_color"] = self.reference_circle[4]["color"]
        result["reference_circle_4_radius_g"] = self.reference_circle[4]["radius_g"]
        result["reference_circle_4_style"] = self.reference_circle[4]["style"]
        result["reference_circle_4_width"] = self.reference_circle[4]["width"]
        result["reference_circle_5_color"] = self.reference_circle[5]["color"]
        result["reference_circle_5_radius_g"] = self.reference_circle[5]["radius_g"]
        result["reference_circle_5_style"] = self.reference_circle[5]["style"]
        result["reference_circle_5_width"] = self.reference_circle[5]["width"]
        result["show_reference_circle"] = True
        result["center_mark_color"] = self.center_mark_color
        result["center_mark_radius_g"] = self.center_mark_radius_g
        result["center_mark_style"] = self.center_mark_style
        result["center_mark_width"] = self.center_mark_width
        result["display_radius_g"] = self.display_radius_g
        result["display_size"] = self.display_size
        result["dot_color"] = self.dot_color
        result["dot_outline_color"] = self.dot_outline_color
        result["dot_outline_width"] = self.dot_outline_width
        result["dot_size"] = self.dot_size
        result["fade_in_radius"] = self.fade_in_radius
        result["fade_out_radius"] = self.fade_out_radius
        result["font_color"] = self.font_color
        result["max_average_lateral_g_circle_color"] = self.max_average_lateral_g_circle_color
        result["max_average_lateral_g_circle_style"] = self.max_average_lateral_g_circle_style
        result["max_average_lateral_g_circle_width"] = self.max_average_lateral_g_circle_width
        result["trace_color"] = self.trace_color
        result["trace_fade_out_step"] = self.trace_fade_out_step
        result["trace_max_samples"] = self.trace_max_samples
        result["trace_style"] = self.trace_style
        result["trace_width"] = self.trace_width
        return result

    @classmethod
    def from_flat(cls, data: Dict[str, Any]) -> "FrictionCircle":
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
        obj.dot = CellConfig.from_flat(data, 'dot')
        obj.fade_out = CellConfig.from_flat(data, 'fade_out')
        obj.highlight = CellConfig.from_flat(data, 'highlight')
        obj.inverted_orientation = CellConfig.from_flat(data, 'inverted_orientation')
        obj.max_average_lateral_g_circle = CellConfig.from_flat(data, 'max_average_lateral_g_circle')
        obj.readings = CellConfig.from_flat(data, 'readings')
        obj.trace = CellConfig.from_flat(data, 'trace')
        obj.trace_fade_out = CellConfig.from_flat(data, 'trace_fade_out')
        obj.reference_circle = {
            1: {"color": data.get("reference_circle_1_color", '#88999999'), "radius_g": data.get("reference_circle_1_radius_g", 1), "style": data.get("reference_circle_1_style", 1), "width": data.get("reference_circle_1_width", 1)},
            2: {"color": data.get("reference_circle_2_color", '#88999999'), "radius_g": data.get("reference_circle_2_radius_g", 2), "style": data.get("reference_circle_2_style", 1), "width": data.get("reference_circle_2_width", 1)},
            3: {"color": data.get("reference_circle_3_color", '#88999999'), "radius_g": data.get("reference_circle_3_radius_g", 3), "style": data.get("reference_circle_3_style", 1), "width": data.get("reference_circle_3_width", 1)},
            4: {"color": data.get("reference_circle_4_color", '#88999999'), "radius_g": data.get("reference_circle_4_radius_g", 4), "style": data.get("reference_circle_4_style", 1), "width": data.get("reference_circle_4_width", 1)},
            5: {"color": data.get("reference_circle_5_color", '#88999999'), "radius_g": data.get("reference_circle_5_radius_g", 5), "style": data.get("reference_circle_5_style", 1), "width": data.get("reference_circle_5_width", 1)},
        }
        obj.center_mark_color = data.get("center_mark_color", obj.center_mark_color)
        obj.center_mark_radius_g = data.get("center_mark_radius_g", obj.center_mark_radius_g)
        obj.center_mark_style = data.get("center_mark_style", obj.center_mark_style)
        obj.center_mark_width = data.get("center_mark_width", obj.center_mark_width)
        obj.display_radius_g = data.get("display_radius_g", obj.display_radius_g)
        obj.display_size = data.get("display_size", obj.display_size)
        obj.dot_color = data.get("dot_color", obj.dot_color)
        obj.dot_outline_color = data.get("dot_outline_color", obj.dot_outline_color)
        obj.dot_outline_width = data.get("dot_outline_width", obj.dot_outline_width)
        obj.dot_size = data.get("dot_size", obj.dot_size)
        obj.fade_in_radius = data.get("fade_in_radius", obj.fade_in_radius)
        obj.fade_out_radius = data.get("fade_out_radius", obj.fade_out_radius)
        obj.font_color = data.get("font_color", obj.font_color)
        obj.max_average_lateral_g_circle_color = data.get("max_average_lateral_g_circle_color", obj.max_average_lateral_g_circle_color)
        obj.max_average_lateral_g_circle_style = data.get("max_average_lateral_g_circle_style", obj.max_average_lateral_g_circle_style)
        obj.max_average_lateral_g_circle_width = data.get("max_average_lateral_g_circle_width", obj.max_average_lateral_g_circle_width)
        obj.trace_color = data.get("trace_color", obj.trace_color)
        obj.trace_fade_out_step = data.get("trace_fade_out_step", obj.trace_fade_out_step)
        obj.trace_max_samples = data.get("trace_max_samples", obj.trace_max_samples)
        obj.trace_style = data.get("trace_style", obj.trace_style)
        obj.trace_width = data.get("trace_width", obj.trace_width)
        return obj

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["font"] = self.font.to_dict()
        result["position"] = self.position.to_dict()
        result["background"] = self.background.to_dict()
        result["center_mark"] = self.center_mark.to_dict()
        result["circle"] = self.circle.to_dict()
        result["circle_background"] = self.circle_background.to_dict()
        result["dot"] = self.dot.to_dict()
        result["fade_out"] = self.fade_out.to_dict()
        result["highlight"] = self.highlight.to_dict()
        result["inverted_orientation"] = self.inverted_orientation.to_dict()
        result["max_average_lateral_g_circle"] = self.max_average_lateral_g_circle.to_dict()
        result["readings"] = self.readings.to_dict()
        result["trace"] = self.trace.to_dict()
        result["trace_fade_out"] = self.trace_fade_out.to_dict()
        result["reference_circle"] = self.reference_circle
        result["center_mark_color"] = self.center_mark_color
        result["center_mark_radius_g"] = self.center_mark_radius_g
        result["center_mark_style"] = self.center_mark_style
        result["center_mark_width"] = self.center_mark_width
        result["display_radius_g"] = self.display_radius_g
        result["display_size"] = self.display_size
        result["dot_color"] = self.dot_color
        result["dot_outline_color"] = self.dot_outline_color
        result["dot_outline_width"] = self.dot_outline_width
        result["dot_size"] = self.dot_size
        result["fade_in_radius"] = self.fade_in_radius
        result["fade_out_radius"] = self.fade_out_radius
        result["font_color"] = self.font_color
        result["max_average_lateral_g_circle_color"] = self.max_average_lateral_g_circle_color
        result["max_average_lateral_g_circle_style"] = self.max_average_lateral_g_circle_style
        result["max_average_lateral_g_circle_width"] = self.max_average_lateral_g_circle_width
        result["trace_color"] = self.trace_color
        result["trace_fade_out_step"] = self.trace_fade_out_step
        result["trace_max_samples"] = self.trace_max_samples
        result["trace_style"] = self.trace_style
        result["trace_width"] = self.trace_width
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FrictionCircle":
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
        obj.dot = CellConfig.from_dict(data.get("dot", {}), 'dot')
        obj.fade_out = CellConfig.from_dict(data.get("fade_out", {}), 'fade_out')
        obj.highlight = CellConfig.from_dict(data.get("highlight", {}), 'highlight')
        obj.inverted_orientation = CellConfig.from_dict(data.get("inverted_orientation", {}), 'inverted_orientation')
        obj.max_average_lateral_g_circle = CellConfig.from_dict(data.get("max_average_lateral_g_circle", {}), 'max_average_lateral_g_circle')
        obj.readings = CellConfig.from_dict(data.get("readings", {}), 'readings')
        obj.trace = CellConfig.from_dict(data.get("trace", {}), 'trace')
        obj.trace_fade_out = CellConfig.from_dict(data.get("trace_fade_out", {}), 'trace_fade_out')
        obj.reference_circle = data.get("reference_circle", obj.reference_circle)
        obj.center_mark_color = data.get("center_mark_color", obj.center_mark_color)
        obj.center_mark_radius_g = data.get("center_mark_radius_g", obj.center_mark_radius_g)
        obj.center_mark_style = data.get("center_mark_style", obj.center_mark_style)
        obj.center_mark_width = data.get("center_mark_width", obj.center_mark_width)
        obj.display_radius_g = data.get("display_radius_g", obj.display_radius_g)
        obj.display_size = data.get("display_size", obj.display_size)
        obj.dot_color = data.get("dot_color", obj.dot_color)
        obj.dot_outline_color = data.get("dot_outline_color", obj.dot_outline_color)
        obj.dot_outline_width = data.get("dot_outline_width", obj.dot_outline_width)
        obj.dot_size = data.get("dot_size", obj.dot_size)
        obj.fade_in_radius = data.get("fade_in_radius", obj.fade_in_radius)
        obj.fade_out_radius = data.get("fade_out_radius", obj.fade_out_radius)
        obj.font_color = data.get("font_color", obj.font_color)
        obj.max_average_lateral_g_circle_color = data.get("max_average_lateral_g_circle_color", obj.max_average_lateral_g_circle_color)
        obj.max_average_lateral_g_circle_style = data.get("max_average_lateral_g_circle_style", obj.max_average_lateral_g_circle_style)
        obj.max_average_lateral_g_circle_width = data.get("max_average_lateral_g_circle_width", obj.max_average_lateral_g_circle_width)
        obj.trace_color = data.get("trace_color", obj.trace_color)
        obj.trace_fade_out_step = data.get("trace_fade_out_step", obj.trace_fade_out_step)
        obj.trace_max_samples = data.get("trace_max_samples", obj.trace_max_samples)
        obj.trace_style = data.get("trace_style", obj.trace_style)
        obj.trace_width = data.get("trace_width", obj.trace_width)
        return obj
