# Auto-generated widget
# Widget: navigation

from dataclasses import dataclass, field
from typing import Any, Dict

from ..base import CellConfig, FontConfig, PositionConfig, WidgetConfig
from ..colors import OVERLAY


@dataclass
class Navigation(WidgetConfig):
    name: str = "navigation"

    # groups
    font: FontConfig = field(default_factory=FontConfig)
    position: PositionConfig = field(default_factory=lambda: PositionConfig(position_x=1040, position_y=70))

    # cells
    background: CellConfig = field(default_factory=lambda: CellConfig(id='background', show=False))
    circle: CellConfig = field(default_factory=lambda: CellConfig(id='circle', font_color=OVERLAY.font_color, bkg_color=OVERLAY.bkg_color))
    circle_background: CellConfig = field(default_factory=lambda: CellConfig(id='circle_background'))
    circle_vehicle_shape: CellConfig = field(default_factory=lambda: CellConfig(id='circle_vehicle_shape', show=False))
    fade_out: CellConfig = field(default_factory=lambda: CellConfig(id='fade_out'))
    sector_line: CellConfig = field(default_factory=lambda: CellConfig(id='sector_line'))
    start_line: CellConfig = field(default_factory=lambda: CellConfig(id='start_line'))
    vehicle_standings: CellConfig = field(default_factory=lambda: CellConfig(id='vehicle_standings', show=False))

    # config
    circle_outline_color: str = '#CCFFFFFF'
    circle_outline_width: int = 0
    display_size: int = 300
    fade_in_radius: float = 0.8
    fade_out_radius: float = 0.98
    font_color: str = '#000000'
    map_color: str = '#FFFFFF'
    map_outline_color: str = '#88000000'
    map_outline_width: int = 2
    map_width: int = 8
    sector_line_color: str = '#00AAFF'
    sector_line_length: int = 12
    sector_line_width: int = 5
    start_line_color: str = '#FF4422'
    start_line_length: int = 12
    start_line_width: int = 6
    vehicle_color_in_pit: str = '#888888'
    vehicle_color_laps_ahead: str = '#FF44CC'
    vehicle_color_laps_behind: str = '#00AAFF'
    vehicle_color_leader: str = '#88FF00'
    vehicle_color_player: str = '#FF4422'
    vehicle_color_same_lap: str = '#FFFFFF'
    vehicle_color_yellow: str = '#FFFF00'
    vehicle_offset: float = 0.8
    vehicle_outline_color: str = '#88000000'
    vehicle_outline_width: int = 1
    vehicle_size: int = 20
    view_radius: int = 500

    def to_flat(self) -> Dict[str, Any]:
        result = super().to_flat()
        result["name"] = self.name
        result.update(self.font.to_flat())
        result.update(self.position.to_flat())
        result.update(self.background.to_flat())
        result.update(self.circle.to_flat())
        result.update(self.circle_background.to_flat())
        result.update(self.circle_vehicle_shape.to_flat())
        result.update(self.fade_out.to_flat())
        result.update(self.sector_line.to_flat())
        result.update(self.start_line.to_flat())
        result.update(self.vehicle_standings.to_flat())
        result["circle_outline_color"] = self.circle_outline_color
        result["circle_outline_width"] = self.circle_outline_width
        result["display_size"] = self.display_size
        result["fade_in_radius"] = self.fade_in_radius
        result["fade_out_radius"] = self.fade_out_radius
        result["font_color"] = self.font_color
        result["map_color"] = self.map_color
        result["map_outline_color"] = self.map_outline_color
        result["map_outline_width"] = self.map_outline_width
        result["map_width"] = self.map_width
        result["sector_line_color"] = self.sector_line_color
        result["sector_line_length"] = self.sector_line_length
        result["sector_line_width"] = self.sector_line_width
        result["start_line_color"] = self.start_line_color
        result["start_line_length"] = self.start_line_length
        result["start_line_width"] = self.start_line_width
        result["vehicle_color_in_pit"] = self.vehicle_color_in_pit
        result["vehicle_color_laps_ahead"] = self.vehicle_color_laps_ahead
        result["vehicle_color_laps_behind"] = self.vehicle_color_laps_behind
        result["vehicle_color_leader"] = self.vehicle_color_leader
        result["vehicle_color_player"] = self.vehicle_color_player
        result["vehicle_color_same_lap"] = self.vehicle_color_same_lap
        result["vehicle_color_yellow"] = self.vehicle_color_yellow
        result["vehicle_offset"] = self.vehicle_offset
        result["vehicle_outline_color"] = self.vehicle_outline_color
        result["vehicle_outline_width"] = self.vehicle_outline_width
        result["vehicle_size"] = self.vehicle_size
        result["view_radius"] = self.view_radius
        return result

    @classmethod
    def from_flat(cls, data: Dict[str, Any]) -> "Navigation":
        obj = cls()
        obj.name = data.get("name", obj.name)
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.font = FontConfig.from_flat(data)
        obj.position = PositionConfig.from_flat(data)
        obj.background = CellConfig.from_flat(data, 'background')
        obj.circle = CellConfig.from_flat(data, 'circle')
        obj.circle_background = CellConfig.from_flat(data, 'circle_background')
        obj.circle_vehicle_shape = CellConfig.from_flat(data, 'circle_vehicle_shape')
        obj.fade_out = CellConfig.from_flat(data, 'fade_out')
        obj.sector_line = CellConfig.from_flat(data, 'sector_line')
        obj.start_line = CellConfig.from_flat(data, 'start_line')
        obj.vehicle_standings = CellConfig.from_flat(data, 'vehicle_standings')
        obj.circle_outline_color = data.get("circle_outline_color", obj.circle_outline_color)
        obj.circle_outline_width = data.get("circle_outline_width", obj.circle_outline_width)
        obj.display_size = data.get("display_size", obj.display_size)
        obj.fade_in_radius = data.get("fade_in_radius", obj.fade_in_radius)
        obj.fade_out_radius = data.get("fade_out_radius", obj.fade_out_radius)
        obj.font_color = data.get("font_color", obj.font_color)
        obj.map_color = data.get("map_color", obj.map_color)
        obj.map_outline_color = data.get("map_outline_color", obj.map_outline_color)
        obj.map_outline_width = data.get("map_outline_width", obj.map_outline_width)
        obj.map_width = data.get("map_width", obj.map_width)
        obj.sector_line_color = data.get("sector_line_color", obj.sector_line_color)
        obj.sector_line_length = data.get("sector_line_length", obj.sector_line_length)
        obj.sector_line_width = data.get("sector_line_width", obj.sector_line_width)
        obj.start_line_color = data.get("start_line_color", obj.start_line_color)
        obj.start_line_length = data.get("start_line_length", obj.start_line_length)
        obj.start_line_width = data.get("start_line_width", obj.start_line_width)
        obj.vehicle_color_in_pit = data.get("vehicle_color_in_pit", obj.vehicle_color_in_pit)
        obj.vehicle_color_laps_ahead = data.get("vehicle_color_laps_ahead", obj.vehicle_color_laps_ahead)
        obj.vehicle_color_laps_behind = data.get("vehicle_color_laps_behind", obj.vehicle_color_laps_behind)
        obj.vehicle_color_leader = data.get("vehicle_color_leader", obj.vehicle_color_leader)
        obj.vehicle_color_player = data.get("vehicle_color_player", obj.vehicle_color_player)
        obj.vehicle_color_same_lap = data.get("vehicle_color_same_lap", obj.vehicle_color_same_lap)
        obj.vehicle_color_yellow = data.get("vehicle_color_yellow", obj.vehicle_color_yellow)
        obj.vehicle_offset = data.get("vehicle_offset", obj.vehicle_offset)
        obj.vehicle_outline_color = data.get("vehicle_outline_color", obj.vehicle_outline_color)
        obj.vehicle_outline_width = data.get("vehicle_outline_width", obj.vehicle_outline_width)
        obj.vehicle_size = data.get("vehicle_size", obj.vehicle_size)
        obj.view_radius = data.get("view_radius", obj.view_radius)
        return obj

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["font"] = self.font.to_dict()
        result["position"] = self.position.to_dict()
        result["background"] = self.background.to_dict()
        result["circle"] = self.circle.to_dict()
        result["circle_background"] = self.circle_background.to_dict()
        result["circle_vehicle_shape"] = self.circle_vehicle_shape.to_dict()
        result["fade_out"] = self.fade_out.to_dict()
        result["sector_line"] = self.sector_line.to_dict()
        result["start_line"] = self.start_line.to_dict()
        result["vehicle_standings"] = self.vehicle_standings.to_dict()
        result["circle_outline_color"] = self.circle_outline_color
        result["circle_outline_width"] = self.circle_outline_width
        result["display_size"] = self.display_size
        result["fade_in_radius"] = self.fade_in_radius
        result["fade_out_radius"] = self.fade_out_radius
        result["font_color"] = self.font_color
        result["map_color"] = self.map_color
        result["map_outline_color"] = self.map_outline_color
        result["map_outline_width"] = self.map_outline_width
        result["map_width"] = self.map_width
        result["sector_line_color"] = self.sector_line_color
        result["sector_line_length"] = self.sector_line_length
        result["sector_line_width"] = self.sector_line_width
        result["start_line_color"] = self.start_line_color
        result["start_line_length"] = self.start_line_length
        result["start_line_width"] = self.start_line_width
        result["vehicle_color_in_pit"] = self.vehicle_color_in_pit
        result["vehicle_color_laps_ahead"] = self.vehicle_color_laps_ahead
        result["vehicle_color_laps_behind"] = self.vehicle_color_laps_behind
        result["vehicle_color_leader"] = self.vehicle_color_leader
        result["vehicle_color_player"] = self.vehicle_color_player
        result["vehicle_color_same_lap"] = self.vehicle_color_same_lap
        result["vehicle_color_yellow"] = self.vehicle_color_yellow
        result["vehicle_offset"] = self.vehicle_offset
        result["vehicle_outline_color"] = self.vehicle_outline_color
        result["vehicle_outline_width"] = self.vehicle_outline_width
        result["vehicle_size"] = self.vehicle_size
        result["view_radius"] = self.view_radius
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Navigation":
        obj = cls()
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.font = FontConfig.from_dict(data.get("font", {}))
        obj.position = PositionConfig.from_dict(data.get("position", {}))
        obj.background = CellConfig.from_dict(data.get("background", {}), 'background')
        obj.circle = CellConfig.from_dict(data.get("circle", {}), 'circle')
        obj.circle_background = CellConfig.from_dict(data.get("circle_background", {}), 'circle_background')
        obj.circle_vehicle_shape = CellConfig.from_dict(data.get("circle_vehicle_shape", {}), 'circle_vehicle_shape')
        obj.fade_out = CellConfig.from_dict(data.get("fade_out", {}), 'fade_out')
        obj.sector_line = CellConfig.from_dict(data.get("sector_line", {}), 'sector_line')
        obj.start_line = CellConfig.from_dict(data.get("start_line", {}), 'start_line')
        obj.vehicle_standings = CellConfig.from_dict(data.get("vehicle_standings", {}), 'vehicle_standings')
        obj.circle_outline_color = data.get("circle_outline_color", obj.circle_outline_color)
        obj.circle_outline_width = data.get("circle_outline_width", obj.circle_outline_width)
        obj.display_size = data.get("display_size", obj.display_size)
        obj.fade_in_radius = data.get("fade_in_radius", obj.fade_in_radius)
        obj.fade_out_radius = data.get("fade_out_radius", obj.fade_out_radius)
        obj.font_color = data.get("font_color", obj.font_color)
        obj.map_color = data.get("map_color", obj.map_color)
        obj.map_outline_color = data.get("map_outline_color", obj.map_outline_color)
        obj.map_outline_width = data.get("map_outline_width", obj.map_outline_width)
        obj.map_width = data.get("map_width", obj.map_width)
        obj.sector_line_color = data.get("sector_line_color", obj.sector_line_color)
        obj.sector_line_length = data.get("sector_line_length", obj.sector_line_length)
        obj.sector_line_width = data.get("sector_line_width", obj.sector_line_width)
        obj.start_line_color = data.get("start_line_color", obj.start_line_color)
        obj.start_line_length = data.get("start_line_length", obj.start_line_length)
        obj.start_line_width = data.get("start_line_width", obj.start_line_width)
        obj.vehicle_color_in_pit = data.get("vehicle_color_in_pit", obj.vehicle_color_in_pit)
        obj.vehicle_color_laps_ahead = data.get("vehicle_color_laps_ahead", obj.vehicle_color_laps_ahead)
        obj.vehicle_color_laps_behind = data.get("vehicle_color_laps_behind", obj.vehicle_color_laps_behind)
        obj.vehicle_color_leader = data.get("vehicle_color_leader", obj.vehicle_color_leader)
        obj.vehicle_color_player = data.get("vehicle_color_player", obj.vehicle_color_player)
        obj.vehicle_color_same_lap = data.get("vehicle_color_same_lap", obj.vehicle_color_same_lap)
        obj.vehicle_color_yellow = data.get("vehicle_color_yellow", obj.vehicle_color_yellow)
        obj.vehicle_offset = data.get("vehicle_offset", obj.vehicle_offset)
        obj.vehicle_outline_color = data.get("vehicle_outline_color", obj.vehicle_outline_color)
        obj.vehicle_outline_width = data.get("vehicle_outline_width", obj.vehicle_outline_width)
        obj.vehicle_size = data.get("vehicle_size", obj.vehicle_size)
        obj.view_radius = data.get("view_radius", obj.view_radius)
        return obj
