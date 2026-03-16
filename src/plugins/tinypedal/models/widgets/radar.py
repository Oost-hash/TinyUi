# Auto-generated widget
# Widget: radar

from dataclasses import dataclass, field
from typing import Any, Dict

from ..base import CellConfig, PositionConfig, WidgetConfig
from ..colors import OVERLAY


@dataclass
class Radar(WidgetConfig):
    name: str = "radar"

    # groups
    position: PositionConfig = field(default_factory=lambda: PositionConfig(position_x=689, position_y=353))

    # cells
    angle_mark: CellConfig = field(default_factory=lambda: CellConfig(id='angle_mark'))
    background: CellConfig = field(default_factory=lambda: CellConfig(id='background', show=False))
    center_mark: CellConfig = field(default_factory=lambda: CellConfig(id='center_mark'))
    circle: CellConfig = field(default_factory=lambda: CellConfig(id='circle', font_color=OVERLAY.font_color, bkg_color=OVERLAY.bkg_color))
    circle_background: CellConfig = field(default_factory=lambda: CellConfig(id='circle_background', show=False))
    edge_fade_out: CellConfig = field(default_factory=lambda: CellConfig(id='edge_fade_out'))
    overlap_indicator: CellConfig = field(default_factory=lambda: CellConfig(id='overlap_indicator'))
    overlap_indicator_in_cone_style: CellConfig = field(default_factory=lambda: CellConfig(id='overlap_indicator_in_cone_style', show=False))
    vehicle_orientation: CellConfig = field(default_factory=lambda: CellConfig(id='vehicle_orientation'))

    # components
    distance_circle: dict = field(default_factory=lambda: {
    1: {'color': '#888888', 'radius': 10, 'style': 0, 'width': 1},
    2: {'color': '#888888', 'radius': 20, 'style': 0, 'width': 1},
    3: {'color': '#888888', 'radius': 30, 'style': 0, 'width': 1},
    4: {'color': '#888888', 'radius': 40, 'style': 0, 'width': 1},
    5: {'color': '#888888', 'radius': 50, 'style': 0, 'width': 1},
})

    # config
    angle_mark_color: str = '#888888'
    angle_mark_radius: int = 30
    angle_mark_style: int = 0
    angle_mark_width: int = 1
    auto_hide: bool = True
    auto_hide_in_private_qualifying: bool = True
    auto_hide_minimum_distance_ahead: int = -1
    auto_hide_minimum_distance_behind: int = -1
    auto_hide_minimum_distance_side: int = -1
    auto_hide_time_threshold: int = 1
    center_mark_color: str = '#888888'
    center_mark_radius: int = 30
    center_mark_style: int = 0
    center_mark_width: int = 1
    edge_fade_in_radius: float = 0.6
    edge_fade_out_radius: float = 0.98
    enable_radar_fade: bool = True
    global_scale: int = 6
    indicator_color_critical: str = '#FF6600'
    indicator_color_nearby: str = '#FFFF00'
    indicator_size_multiplier: int = 8
    overlap_cone_angle: int = 120
    overlap_critical_range_multiplier: int = 1
    overlap_nearby_range_multiplier: int = 5
    radar_fade_in_radius: float = 0.8
    radar_fade_out_radius: float = 0.98
    radar_radius: int = 30
    vehicle_border_radius: int = 2
    vehicle_color_in_pit: str = '#888888'
    vehicle_color_laps_ahead: str = '#FF44CC'
    vehicle_color_laps_behind: str = '#00AAFF'
    vehicle_color_leader: str = '#88FF00'
    vehicle_color_player: str = '#FF4422'
    vehicle_color_same_lap: str = '#FFFFFF'
    vehicle_color_yellow: str = '#FFFF00'
    vehicle_length: float = 4.6
    vehicle_maximum_visible_distance_ahead: int = -1
    vehicle_maximum_visible_distance_behind: int = -1
    vehicle_maximum_visible_distance_side: int = -1
    vehicle_outline_color: str = '#88000000'
    vehicle_outline_width: int = 1
    vehicle_width: float = 2.2

    def to_flat(self) -> Dict[str, Any]:
        result = super().to_flat()
        result["name"] = self.name
        result.update(self.position.to_flat())
        result.update(self.angle_mark.to_flat())
        result.update(self.background.to_flat())
        result.update(self.center_mark.to_flat())
        result.update(self.circle.to_flat())
        result.update(self.circle_background.to_flat())
        result.update(self.edge_fade_out.to_flat())
        result.update(self.overlap_indicator.to_flat())
        result.update(self.overlap_indicator_in_cone_style.to_flat())
        result.update(self.vehicle_orientation.to_flat())
        result["distance_circle_1_color"] = self.distance_circle[1]["color"]
        result["distance_circle_1_radius"] = self.distance_circle[1]["radius"]
        result["distance_circle_1_style"] = self.distance_circle[1]["style"]
        result["distance_circle_1_width"] = self.distance_circle[1]["width"]
        result["distance_circle_2_color"] = self.distance_circle[2]["color"]
        result["distance_circle_2_radius"] = self.distance_circle[2]["radius"]
        result["distance_circle_2_style"] = self.distance_circle[2]["style"]
        result["distance_circle_2_width"] = self.distance_circle[2]["width"]
        result["distance_circle_3_color"] = self.distance_circle[3]["color"]
        result["distance_circle_3_radius"] = self.distance_circle[3]["radius"]
        result["distance_circle_3_style"] = self.distance_circle[3]["style"]
        result["distance_circle_3_width"] = self.distance_circle[3]["width"]
        result["distance_circle_4_color"] = self.distance_circle[4]["color"]
        result["distance_circle_4_radius"] = self.distance_circle[4]["radius"]
        result["distance_circle_4_style"] = self.distance_circle[4]["style"]
        result["distance_circle_4_width"] = self.distance_circle[4]["width"]
        result["distance_circle_5_color"] = self.distance_circle[5]["color"]
        result["distance_circle_5_radius"] = self.distance_circle[5]["radius"]
        result["distance_circle_5_style"] = self.distance_circle[5]["style"]
        result["distance_circle_5_width"] = self.distance_circle[5]["width"]
        result["show_distance_circle"] = True
        result["angle_mark_color"] = self.angle_mark_color
        result["angle_mark_radius"] = self.angle_mark_radius
        result["angle_mark_style"] = self.angle_mark_style
        result["angle_mark_width"] = self.angle_mark_width
        result["auto_hide"] = self.auto_hide
        result["auto_hide_in_private_qualifying"] = self.auto_hide_in_private_qualifying
        result["auto_hide_minimum_distance_ahead"] = self.auto_hide_minimum_distance_ahead
        result["auto_hide_minimum_distance_behind"] = self.auto_hide_minimum_distance_behind
        result["auto_hide_minimum_distance_side"] = self.auto_hide_minimum_distance_side
        result["auto_hide_time_threshold"] = self.auto_hide_time_threshold
        result["center_mark_color"] = self.center_mark_color
        result["center_mark_radius"] = self.center_mark_radius
        result["center_mark_style"] = self.center_mark_style
        result["center_mark_width"] = self.center_mark_width
        result["edge_fade_in_radius"] = self.edge_fade_in_radius
        result["edge_fade_out_radius"] = self.edge_fade_out_radius
        result["enable_radar_fade"] = self.enable_radar_fade
        result["global_scale"] = self.global_scale
        result["indicator_color_critical"] = self.indicator_color_critical
        result["indicator_color_nearby"] = self.indicator_color_nearby
        result["indicator_size_multiplier"] = self.indicator_size_multiplier
        result["overlap_cone_angle"] = self.overlap_cone_angle
        result["overlap_critical_range_multiplier"] = self.overlap_critical_range_multiplier
        result["overlap_nearby_range_multiplier"] = self.overlap_nearby_range_multiplier
        result["radar_fade_in_radius"] = self.radar_fade_in_radius
        result["radar_fade_out_radius"] = self.radar_fade_out_radius
        result["radar_radius"] = self.radar_radius
        result["vehicle_border_radius"] = self.vehicle_border_radius
        result["vehicle_color_in_pit"] = self.vehicle_color_in_pit
        result["vehicle_color_laps_ahead"] = self.vehicle_color_laps_ahead
        result["vehicle_color_laps_behind"] = self.vehicle_color_laps_behind
        result["vehicle_color_leader"] = self.vehicle_color_leader
        result["vehicle_color_player"] = self.vehicle_color_player
        result["vehicle_color_same_lap"] = self.vehicle_color_same_lap
        result["vehicle_color_yellow"] = self.vehicle_color_yellow
        result["vehicle_length"] = self.vehicle_length
        result["vehicle_maximum_visible_distance_ahead"] = self.vehicle_maximum_visible_distance_ahead
        result["vehicle_maximum_visible_distance_behind"] = self.vehicle_maximum_visible_distance_behind
        result["vehicle_maximum_visible_distance_side"] = self.vehicle_maximum_visible_distance_side
        result["vehicle_outline_color"] = self.vehicle_outline_color
        result["vehicle_outline_width"] = self.vehicle_outline_width
        result["vehicle_width"] = self.vehicle_width
        return result

    @classmethod
    def from_flat(cls, data: Dict[str, Any]) -> "Radar":
        obj = cls()
        obj.name = data.get("name", obj.name)
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.position = PositionConfig.from_flat(data)
        obj.angle_mark = CellConfig.from_flat(data, 'angle_mark')
        obj.background = CellConfig.from_flat(data, 'background')
        obj.center_mark = CellConfig.from_flat(data, 'center_mark')
        obj.circle = CellConfig.from_flat(data, 'circle')
        obj.circle_background = CellConfig.from_flat(data, 'circle_background')
        obj.edge_fade_out = CellConfig.from_flat(data, 'edge_fade_out')
        obj.overlap_indicator = CellConfig.from_flat(data, 'overlap_indicator')
        obj.overlap_indicator_in_cone_style = CellConfig.from_flat(data, 'overlap_indicator_in_cone_style')
        obj.vehicle_orientation = CellConfig.from_flat(data, 'vehicle_orientation')
        obj.distance_circle = {
            1: {"color": data.get("distance_circle_1_color", '#888888'), "radius": data.get("distance_circle_1_radius", 10), "style": data.get("distance_circle_1_style", 0), "width": data.get("distance_circle_1_width", 1)},
            2: {"color": data.get("distance_circle_2_color", '#888888'), "radius": data.get("distance_circle_2_radius", 20), "style": data.get("distance_circle_2_style", 0), "width": data.get("distance_circle_2_width", 1)},
            3: {"color": data.get("distance_circle_3_color", '#888888'), "radius": data.get("distance_circle_3_radius", 30), "style": data.get("distance_circle_3_style", 0), "width": data.get("distance_circle_3_width", 1)},
            4: {"color": data.get("distance_circle_4_color", '#888888'), "radius": data.get("distance_circle_4_radius", 40), "style": data.get("distance_circle_4_style", 0), "width": data.get("distance_circle_4_width", 1)},
            5: {"color": data.get("distance_circle_5_color", '#888888'), "radius": data.get("distance_circle_5_radius", 50), "style": data.get("distance_circle_5_style", 0), "width": data.get("distance_circle_5_width", 1)},
        }
        obj.angle_mark_color = data.get("angle_mark_color", obj.angle_mark_color)
        obj.angle_mark_radius = data.get("angle_mark_radius", obj.angle_mark_radius)
        obj.angle_mark_style = data.get("angle_mark_style", obj.angle_mark_style)
        obj.angle_mark_width = data.get("angle_mark_width", obj.angle_mark_width)
        obj.auto_hide = data.get("auto_hide", obj.auto_hide)
        obj.auto_hide_in_private_qualifying = data.get("auto_hide_in_private_qualifying", obj.auto_hide_in_private_qualifying)
        obj.auto_hide_minimum_distance_ahead = data.get("auto_hide_minimum_distance_ahead", obj.auto_hide_minimum_distance_ahead)
        obj.auto_hide_minimum_distance_behind = data.get("auto_hide_minimum_distance_behind", obj.auto_hide_minimum_distance_behind)
        obj.auto_hide_minimum_distance_side = data.get("auto_hide_minimum_distance_side", obj.auto_hide_minimum_distance_side)
        obj.auto_hide_time_threshold = data.get("auto_hide_time_threshold", obj.auto_hide_time_threshold)
        obj.center_mark_color = data.get("center_mark_color", obj.center_mark_color)
        obj.center_mark_radius = data.get("center_mark_radius", obj.center_mark_radius)
        obj.center_mark_style = data.get("center_mark_style", obj.center_mark_style)
        obj.center_mark_width = data.get("center_mark_width", obj.center_mark_width)
        obj.edge_fade_in_radius = data.get("edge_fade_in_radius", obj.edge_fade_in_radius)
        obj.edge_fade_out_radius = data.get("edge_fade_out_radius", obj.edge_fade_out_radius)
        obj.enable_radar_fade = data.get("enable_radar_fade", obj.enable_radar_fade)
        obj.global_scale = data.get("global_scale", obj.global_scale)
        obj.indicator_color_critical = data.get("indicator_color_critical", obj.indicator_color_critical)
        obj.indicator_color_nearby = data.get("indicator_color_nearby", obj.indicator_color_nearby)
        obj.indicator_size_multiplier = data.get("indicator_size_multiplier", obj.indicator_size_multiplier)
        obj.overlap_cone_angle = data.get("overlap_cone_angle", obj.overlap_cone_angle)
        obj.overlap_critical_range_multiplier = data.get("overlap_critical_range_multiplier", obj.overlap_critical_range_multiplier)
        obj.overlap_nearby_range_multiplier = data.get("overlap_nearby_range_multiplier", obj.overlap_nearby_range_multiplier)
        obj.radar_fade_in_radius = data.get("radar_fade_in_radius", obj.radar_fade_in_radius)
        obj.radar_fade_out_radius = data.get("radar_fade_out_radius", obj.radar_fade_out_radius)
        obj.radar_radius = data.get("radar_radius", obj.radar_radius)
        obj.vehicle_border_radius = data.get("vehicle_border_radius", obj.vehicle_border_radius)
        obj.vehicle_color_in_pit = data.get("vehicle_color_in_pit", obj.vehicle_color_in_pit)
        obj.vehicle_color_laps_ahead = data.get("vehicle_color_laps_ahead", obj.vehicle_color_laps_ahead)
        obj.vehicle_color_laps_behind = data.get("vehicle_color_laps_behind", obj.vehicle_color_laps_behind)
        obj.vehicle_color_leader = data.get("vehicle_color_leader", obj.vehicle_color_leader)
        obj.vehicle_color_player = data.get("vehicle_color_player", obj.vehicle_color_player)
        obj.vehicle_color_same_lap = data.get("vehicle_color_same_lap", obj.vehicle_color_same_lap)
        obj.vehicle_color_yellow = data.get("vehicle_color_yellow", obj.vehicle_color_yellow)
        obj.vehicle_length = data.get("vehicle_length", obj.vehicle_length)
        obj.vehicle_maximum_visible_distance_ahead = data.get("vehicle_maximum_visible_distance_ahead", obj.vehicle_maximum_visible_distance_ahead)
        obj.vehicle_maximum_visible_distance_behind = data.get("vehicle_maximum_visible_distance_behind", obj.vehicle_maximum_visible_distance_behind)
        obj.vehicle_maximum_visible_distance_side = data.get("vehicle_maximum_visible_distance_side", obj.vehicle_maximum_visible_distance_side)
        obj.vehicle_outline_color = data.get("vehicle_outline_color", obj.vehicle_outline_color)
        obj.vehicle_outline_width = data.get("vehicle_outline_width", obj.vehicle_outline_width)
        obj.vehicle_width = data.get("vehicle_width", obj.vehicle_width)
        return obj

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["position"] = self.position.to_dict()
        result["angle_mark"] = self.angle_mark.to_dict()
        result["background"] = self.background.to_dict()
        result["center_mark"] = self.center_mark.to_dict()
        result["circle"] = self.circle.to_dict()
        result["circle_background"] = self.circle_background.to_dict()
        result["edge_fade_out"] = self.edge_fade_out.to_dict()
        result["overlap_indicator"] = self.overlap_indicator.to_dict()
        result["overlap_indicator_in_cone_style"] = self.overlap_indicator_in_cone_style.to_dict()
        result["vehicle_orientation"] = self.vehicle_orientation.to_dict()
        result["distance_circle"] = self.distance_circle
        result["angle_mark_color"] = self.angle_mark_color
        result["angle_mark_radius"] = self.angle_mark_radius
        result["angle_mark_style"] = self.angle_mark_style
        result["angle_mark_width"] = self.angle_mark_width
        result["auto_hide"] = self.auto_hide
        result["auto_hide_in_private_qualifying"] = self.auto_hide_in_private_qualifying
        result["auto_hide_minimum_distance_ahead"] = self.auto_hide_minimum_distance_ahead
        result["auto_hide_minimum_distance_behind"] = self.auto_hide_minimum_distance_behind
        result["auto_hide_minimum_distance_side"] = self.auto_hide_minimum_distance_side
        result["auto_hide_time_threshold"] = self.auto_hide_time_threshold
        result["center_mark_color"] = self.center_mark_color
        result["center_mark_radius"] = self.center_mark_radius
        result["center_mark_style"] = self.center_mark_style
        result["center_mark_width"] = self.center_mark_width
        result["edge_fade_in_radius"] = self.edge_fade_in_radius
        result["edge_fade_out_radius"] = self.edge_fade_out_radius
        result["enable_radar_fade"] = self.enable_radar_fade
        result["global_scale"] = self.global_scale
        result["indicator_color_critical"] = self.indicator_color_critical
        result["indicator_color_nearby"] = self.indicator_color_nearby
        result["indicator_size_multiplier"] = self.indicator_size_multiplier
        result["overlap_cone_angle"] = self.overlap_cone_angle
        result["overlap_critical_range_multiplier"] = self.overlap_critical_range_multiplier
        result["overlap_nearby_range_multiplier"] = self.overlap_nearby_range_multiplier
        result["radar_fade_in_radius"] = self.radar_fade_in_radius
        result["radar_fade_out_radius"] = self.radar_fade_out_radius
        result["radar_radius"] = self.radar_radius
        result["vehicle_border_radius"] = self.vehicle_border_radius
        result["vehicle_color_in_pit"] = self.vehicle_color_in_pit
        result["vehicle_color_laps_ahead"] = self.vehicle_color_laps_ahead
        result["vehicle_color_laps_behind"] = self.vehicle_color_laps_behind
        result["vehicle_color_leader"] = self.vehicle_color_leader
        result["vehicle_color_player"] = self.vehicle_color_player
        result["vehicle_color_same_lap"] = self.vehicle_color_same_lap
        result["vehicle_color_yellow"] = self.vehicle_color_yellow
        result["vehicle_length"] = self.vehicle_length
        result["vehicle_maximum_visible_distance_ahead"] = self.vehicle_maximum_visible_distance_ahead
        result["vehicle_maximum_visible_distance_behind"] = self.vehicle_maximum_visible_distance_behind
        result["vehicle_maximum_visible_distance_side"] = self.vehicle_maximum_visible_distance_side
        result["vehicle_outline_color"] = self.vehicle_outline_color
        result["vehicle_outline_width"] = self.vehicle_outline_width
        result["vehicle_width"] = self.vehicle_width
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Radar":
        obj = cls()
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.position = PositionConfig.from_dict(data.get("position", {}))
        obj.angle_mark = CellConfig.from_dict(data.get("angle_mark", {}), 'angle_mark')
        obj.background = CellConfig.from_dict(data.get("background", {}), 'background')
        obj.center_mark = CellConfig.from_dict(data.get("center_mark", {}), 'center_mark')
        obj.circle = CellConfig.from_dict(data.get("circle", {}), 'circle')
        obj.circle_background = CellConfig.from_dict(data.get("circle_background", {}), 'circle_background')
        obj.edge_fade_out = CellConfig.from_dict(data.get("edge_fade_out", {}), 'edge_fade_out')
        obj.overlap_indicator = CellConfig.from_dict(data.get("overlap_indicator", {}), 'overlap_indicator')
        obj.overlap_indicator_in_cone_style = CellConfig.from_dict(data.get("overlap_indicator_in_cone_style", {}), 'overlap_indicator_in_cone_style')
        obj.vehicle_orientation = CellConfig.from_dict(data.get("vehicle_orientation", {}), 'vehicle_orientation')
        obj.distance_circle = data.get("distance_circle", obj.distance_circle)
        obj.angle_mark_color = data.get("angle_mark_color", obj.angle_mark_color)
        obj.angle_mark_radius = data.get("angle_mark_radius", obj.angle_mark_radius)
        obj.angle_mark_style = data.get("angle_mark_style", obj.angle_mark_style)
        obj.angle_mark_width = data.get("angle_mark_width", obj.angle_mark_width)
        obj.auto_hide = data.get("auto_hide", obj.auto_hide)
        obj.auto_hide_in_private_qualifying = data.get("auto_hide_in_private_qualifying", obj.auto_hide_in_private_qualifying)
        obj.auto_hide_minimum_distance_ahead = data.get("auto_hide_minimum_distance_ahead", obj.auto_hide_minimum_distance_ahead)
        obj.auto_hide_minimum_distance_behind = data.get("auto_hide_minimum_distance_behind", obj.auto_hide_minimum_distance_behind)
        obj.auto_hide_minimum_distance_side = data.get("auto_hide_minimum_distance_side", obj.auto_hide_minimum_distance_side)
        obj.auto_hide_time_threshold = data.get("auto_hide_time_threshold", obj.auto_hide_time_threshold)
        obj.center_mark_color = data.get("center_mark_color", obj.center_mark_color)
        obj.center_mark_radius = data.get("center_mark_radius", obj.center_mark_radius)
        obj.center_mark_style = data.get("center_mark_style", obj.center_mark_style)
        obj.center_mark_width = data.get("center_mark_width", obj.center_mark_width)
        obj.edge_fade_in_radius = data.get("edge_fade_in_radius", obj.edge_fade_in_radius)
        obj.edge_fade_out_radius = data.get("edge_fade_out_radius", obj.edge_fade_out_radius)
        obj.enable_radar_fade = data.get("enable_radar_fade", obj.enable_radar_fade)
        obj.global_scale = data.get("global_scale", obj.global_scale)
        obj.indicator_color_critical = data.get("indicator_color_critical", obj.indicator_color_critical)
        obj.indicator_color_nearby = data.get("indicator_color_nearby", obj.indicator_color_nearby)
        obj.indicator_size_multiplier = data.get("indicator_size_multiplier", obj.indicator_size_multiplier)
        obj.overlap_cone_angle = data.get("overlap_cone_angle", obj.overlap_cone_angle)
        obj.overlap_critical_range_multiplier = data.get("overlap_critical_range_multiplier", obj.overlap_critical_range_multiplier)
        obj.overlap_nearby_range_multiplier = data.get("overlap_nearby_range_multiplier", obj.overlap_nearby_range_multiplier)
        obj.radar_fade_in_radius = data.get("radar_fade_in_radius", obj.radar_fade_in_radius)
        obj.radar_fade_out_radius = data.get("radar_fade_out_radius", obj.radar_fade_out_radius)
        obj.radar_radius = data.get("radar_radius", obj.radar_radius)
        obj.vehicle_border_radius = data.get("vehicle_border_radius", obj.vehicle_border_radius)
        obj.vehicle_color_in_pit = data.get("vehicle_color_in_pit", obj.vehicle_color_in_pit)
        obj.vehicle_color_laps_ahead = data.get("vehicle_color_laps_ahead", obj.vehicle_color_laps_ahead)
        obj.vehicle_color_laps_behind = data.get("vehicle_color_laps_behind", obj.vehicle_color_laps_behind)
        obj.vehicle_color_leader = data.get("vehicle_color_leader", obj.vehicle_color_leader)
        obj.vehicle_color_player = data.get("vehicle_color_player", obj.vehicle_color_player)
        obj.vehicle_color_same_lap = data.get("vehicle_color_same_lap", obj.vehicle_color_same_lap)
        obj.vehicle_color_yellow = data.get("vehicle_color_yellow", obj.vehicle_color_yellow)
        obj.vehicle_length = data.get("vehicle_length", obj.vehicle_length)
        obj.vehicle_maximum_visible_distance_ahead = data.get("vehicle_maximum_visible_distance_ahead", obj.vehicle_maximum_visible_distance_ahead)
        obj.vehicle_maximum_visible_distance_behind = data.get("vehicle_maximum_visible_distance_behind", obj.vehicle_maximum_visible_distance_behind)
        obj.vehicle_maximum_visible_distance_side = data.get("vehicle_maximum_visible_distance_side", obj.vehicle_maximum_visible_distance_side)
        obj.vehicle_outline_color = data.get("vehicle_outline_color", obj.vehicle_outline_color)
        obj.vehicle_outline_width = data.get("vehicle_outline_width", obj.vehicle_outline_width)
        obj.vehicle_width = data.get("vehicle_width", obj.vehicle_width)
        return obj
