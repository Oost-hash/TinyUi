# Auto-generated widget
# Widget: track_map

from dataclasses import dataclass, field
from typing import Any, Dict

from ..base import CellConfig, FontConfig, PositionConfig, WidgetConfig


@dataclass
class TrackMap(WidgetConfig):
    name: str = "track_map"

    # base overrides
    bar_padding: float = 0.5

    # groups
    font: FontConfig = field(default_factory=FontConfig)
    position: PositionConfig = field(default_factory=lambda: PositionConfig(position_x=663, position_y=25))

    # cells
    background: CellConfig = field(default_factory=lambda: CellConfig(id='background', show=False))
    custom_player_color_in_multi_class: CellConfig = field(default_factory=lambda: CellConfig(id='custom_player_color_in_multi_class', show=False))
    lap_difference_outline: CellConfig = field(default_factory=lambda: CellConfig(id='lap_difference_outline', show=False))
    map: CellConfig = field(default_factory=lambda: CellConfig(id='map', bkg_color='#88000000'))
    map_background: CellConfig = field(default_factory=lambda: CellConfig(id='map_background', show=False))
    pitout_prediction: CellConfig = field(default_factory=lambda: CellConfig(id='pitout_prediction'))
    pitout_prediction_while_requested_pitstop: CellConfig = field(default_factory=lambda: CellConfig(id='pitout_prediction_while_requested_pitstop'))
    pitstop_duration: CellConfig = field(default_factory=lambda: CellConfig(id='pitstop_duration', bkg_color='#AA000000'))
    player: CellConfig = field(default_factory=lambda: CellConfig(id='player'))
    position_in_class: CellConfig = field(default_factory=lambda: CellConfig(id='position_in_class'))
    proximity_circle: CellConfig = field(default_factory=lambda: CellConfig(id='proximity_circle'))
    sector_line: CellConfig = field(default_factory=lambda: CellConfig(id='sector_line'))
    start_line: CellConfig = field(default_factory=lambda: CellConfig(id='start_line'))
    vehicle_standings: CellConfig = field(default_factory=lambda: CellConfig(id='vehicle_standings'))

    # components
    fixed_pitstop_duration: dict = field(default_factory=lambda: {
    1: 0,
    2: 10,
    3: 25,
    4: 40,
    5: 45,
    6: 52,
    7: 100,
    8: 120,
    9: 180,
    10: -1,
})

    # config
    area_margin: int = 40
    area_size: int = 400
    display_detail_level: int = 1
    display_orientation: int = 0
    enable_multi_class_styling: bool = True
    enabled_fixed_pitout_prediction: bool = False
    font_color: str = '#000000'
    map_color: str = '#FFFFFF'
    map_outline_color: str = '#88000000'
    map_outline_width: int = 2
    map_width: int = 5
    number_of_prediction: int = 6
    pitout_duration_increment: int = 10
    pitout_duration_minimum: int = 15
    pitout_time_offset: int = 3
    prediction_outline_color: str = '#BBFF0000'
    prediction_outline_width: int = 3
    proximity_circle_color: str = '#88888888'
    proximity_circle_radius: int = 150
    proximity_circle_width: int = 3
    sector_line_color: str = '#00AAFF'
    sector_line_length: int = 7
    sector_line_width: int = 3
    start_line_color: str = '#FF4422'
    start_line_length: int = 8
    start_line_width: int = 4
    vehicle_color_in_pit: str = '#888888'
    vehicle_color_laps_ahead: str = '#FF44CC'
    vehicle_color_laps_behind: str = '#00AAFF'
    vehicle_color_leader: str = '#88FF00'
    vehicle_color_player: str = '#FF4422'
    vehicle_color_same_lap: str = '#FFFFFF'
    vehicle_color_yellow: str = '#FFFF00'
    vehicle_outline_color: str = '#88000000'
    vehicle_outline_color_laps_ahead: str = '#FF44CC'
    vehicle_outline_color_laps_behind: str = '#00AAFF'
    vehicle_outline_player_color: str = '#AAFFFFFF'
    vehicle_outline_player_width: int = 2
    vehicle_outline_width: int = 1
    vehicle_outline_width_laps_ahead: int = 2
    vehicle_outline_width_laps_behind: int = 2
    vehicle_scale: int = 1
    vehicle_scale_player: int = 1

    def to_flat(self) -> Dict[str, Any]:
        result = super().to_flat()
        result["name"] = self.name
        result["bar_padding"] = self.bar_padding
        result.update(self.font.to_flat())
        result.update(self.position.to_flat())
        result.update(self.background.to_flat())
        result.update(self.custom_player_color_in_multi_class.to_flat())
        result.update(self.lap_difference_outline.to_flat())
        result.update(self.map.to_flat())
        result.update(self.map_background.to_flat())
        result.update(self.pitout_prediction.to_flat())
        result.update(self.pitout_prediction_while_requested_pitstop.to_flat())
        result.update(self.pitstop_duration.to_flat())
        result.update(self.player.to_flat())
        result.update(self.position_in_class.to_flat())
        result.update(self.proximity_circle.to_flat())
        result.update(self.sector_line.to_flat())
        result.update(self.start_line.to_flat())
        result.update(self.vehicle_standings.to_flat())
        result["fixed_pitstop_duration_1"] = self.fixed_pitstop_duration[1]
        result["fixed_pitstop_duration_2"] = self.fixed_pitstop_duration[2]
        result["fixed_pitstop_duration_3"] = self.fixed_pitstop_duration[3]
        result["fixed_pitstop_duration_4"] = self.fixed_pitstop_duration[4]
        result["fixed_pitstop_duration_5"] = self.fixed_pitstop_duration[5]
        result["fixed_pitstop_duration_6"] = self.fixed_pitstop_duration[6]
        result["fixed_pitstop_duration_7"] = self.fixed_pitstop_duration[7]
        result["fixed_pitstop_duration_8"] = self.fixed_pitstop_duration[8]
        result["fixed_pitstop_duration_9"] = self.fixed_pitstop_duration[9]
        result["fixed_pitstop_duration_10"] = self.fixed_pitstop_duration[10]
        result["area_margin"] = self.area_margin
        result["area_size"] = self.area_size
        result["display_detail_level"] = self.display_detail_level
        result["display_orientation"] = self.display_orientation
        result["enable_multi_class_styling"] = self.enable_multi_class_styling
        result["enabled_fixed_pitout_prediction"] = self.enabled_fixed_pitout_prediction
        result["font_color"] = self.font_color
        result["map_color"] = self.map_color
        result["map_outline_color"] = self.map_outline_color
        result["map_outline_width"] = self.map_outline_width
        result["map_width"] = self.map_width
        result["number_of_prediction"] = self.number_of_prediction
        result["pitout_duration_increment"] = self.pitout_duration_increment
        result["pitout_duration_minimum"] = self.pitout_duration_minimum
        result["pitout_time_offset"] = self.pitout_time_offset
        result["prediction_outline_color"] = self.prediction_outline_color
        result["prediction_outline_width"] = self.prediction_outline_width
        result["proximity_circle_color"] = self.proximity_circle_color
        result["proximity_circle_radius"] = self.proximity_circle_radius
        result["proximity_circle_width"] = self.proximity_circle_width
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
        result["vehicle_outline_color"] = self.vehicle_outline_color
        result["vehicle_outline_color_laps_ahead"] = self.vehicle_outline_color_laps_ahead
        result["vehicle_outline_color_laps_behind"] = self.vehicle_outline_color_laps_behind
        result["vehicle_outline_player_color"] = self.vehicle_outline_player_color
        result["vehicle_outline_player_width"] = self.vehicle_outline_player_width
        result["vehicle_outline_width"] = self.vehicle_outline_width
        result["vehicle_outline_width_laps_ahead"] = self.vehicle_outline_width_laps_ahead
        result["vehicle_outline_width_laps_behind"] = self.vehicle_outline_width_laps_behind
        result["vehicle_scale"] = self.vehicle_scale
        result["vehicle_scale_player"] = self.vehicle_scale_player
        return result

    @classmethod
    def from_flat(cls, data: Dict[str, Any]) -> "TrackMap":
        obj = cls()
        obj.name = data.get("name", obj.name)
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.bar_padding = data.get("bar_padding", obj.bar_padding)
        obj.font = FontConfig.from_flat(data)
        obj.position = PositionConfig.from_flat(data)
        obj.background = CellConfig.from_flat(data, 'background')
        obj.custom_player_color_in_multi_class = CellConfig.from_flat(data, 'custom_player_color_in_multi_class')
        obj.lap_difference_outline = CellConfig.from_flat(data, 'lap_difference_outline')
        obj.map = CellConfig.from_flat(data, 'map')
        obj.map_background = CellConfig.from_flat(data, 'map_background')
        obj.pitout_prediction = CellConfig.from_flat(data, 'pitout_prediction')
        obj.pitout_prediction_while_requested_pitstop = CellConfig.from_flat(data, 'pitout_prediction_while_requested_pitstop')
        obj.pitstop_duration = CellConfig.from_flat(data, 'pitstop_duration')
        obj.player = CellConfig.from_flat(data, 'player')
        obj.position_in_class = CellConfig.from_flat(data, 'position_in_class')
        obj.proximity_circle = CellConfig.from_flat(data, 'proximity_circle')
        obj.sector_line = CellConfig.from_flat(data, 'sector_line')
        obj.start_line = CellConfig.from_flat(data, 'start_line')
        obj.vehicle_standings = CellConfig.from_flat(data, 'vehicle_standings')
        obj.fixed_pitstop_duration = {
            1: data.get("fixed_pitstop_duration_1", 0),
            2: data.get("fixed_pitstop_duration_2", 10),
            3: data.get("fixed_pitstop_duration_3", 25),
            4: data.get("fixed_pitstop_duration_4", 40),
            5: data.get("fixed_pitstop_duration_5", 45),
            6: data.get("fixed_pitstop_duration_6", 52),
            7: data.get("fixed_pitstop_duration_7", 100),
            8: data.get("fixed_pitstop_duration_8", 120),
            9: data.get("fixed_pitstop_duration_9", 180),
            10: data.get("fixed_pitstop_duration_10", -1),
        }
        obj.area_margin = data.get("area_margin", obj.area_margin)
        obj.area_size = data.get("area_size", obj.area_size)
        obj.display_detail_level = data.get("display_detail_level", obj.display_detail_level)
        obj.display_orientation = data.get("display_orientation", obj.display_orientation)
        obj.enable_multi_class_styling = data.get("enable_multi_class_styling", obj.enable_multi_class_styling)
        obj.enabled_fixed_pitout_prediction = data.get("enabled_fixed_pitout_prediction", obj.enabled_fixed_pitout_prediction)
        obj.font_color = data.get("font_color", obj.font_color)
        obj.map_color = data.get("map_color", obj.map_color)
        obj.map_outline_color = data.get("map_outline_color", obj.map_outline_color)
        obj.map_outline_width = data.get("map_outline_width", obj.map_outline_width)
        obj.map_width = data.get("map_width", obj.map_width)
        obj.number_of_prediction = data.get("number_of_prediction", obj.number_of_prediction)
        obj.pitout_duration_increment = data.get("pitout_duration_increment", obj.pitout_duration_increment)
        obj.pitout_duration_minimum = data.get("pitout_duration_minimum", obj.pitout_duration_minimum)
        obj.pitout_time_offset = data.get("pitout_time_offset", obj.pitout_time_offset)
        obj.prediction_outline_color = data.get("prediction_outline_color", obj.prediction_outline_color)
        obj.prediction_outline_width = data.get("prediction_outline_width", obj.prediction_outline_width)
        obj.proximity_circle_color = data.get("proximity_circle_color", obj.proximity_circle_color)
        obj.proximity_circle_radius = data.get("proximity_circle_radius", obj.proximity_circle_radius)
        obj.proximity_circle_width = data.get("proximity_circle_width", obj.proximity_circle_width)
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
        obj.vehicle_outline_color = data.get("vehicle_outline_color", obj.vehicle_outline_color)
        obj.vehicle_outline_color_laps_ahead = data.get("vehicle_outline_color_laps_ahead", obj.vehicle_outline_color_laps_ahead)
        obj.vehicle_outline_color_laps_behind = data.get("vehicle_outline_color_laps_behind", obj.vehicle_outline_color_laps_behind)
        obj.vehicle_outline_player_color = data.get("vehicle_outline_player_color", obj.vehicle_outline_player_color)
        obj.vehicle_outline_player_width = data.get("vehicle_outline_player_width", obj.vehicle_outline_player_width)
        obj.vehicle_outline_width = data.get("vehicle_outline_width", obj.vehicle_outline_width)
        obj.vehicle_outline_width_laps_ahead = data.get("vehicle_outline_width_laps_ahead", obj.vehicle_outline_width_laps_ahead)
        obj.vehicle_outline_width_laps_behind = data.get("vehicle_outline_width_laps_behind", obj.vehicle_outline_width_laps_behind)
        obj.vehicle_scale = data.get("vehicle_scale", obj.vehicle_scale)
        obj.vehicle_scale_player = data.get("vehicle_scale_player", obj.vehicle_scale_player)
        return obj

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["bar_padding"] = self.bar_padding
        result["font"] = self.font.to_dict()
        result["position"] = self.position.to_dict()
        result["background"] = self.background.to_dict()
        result["custom_player_color_in_multi_class"] = self.custom_player_color_in_multi_class.to_dict()
        result["lap_difference_outline"] = self.lap_difference_outline.to_dict()
        result["map"] = self.map.to_dict()
        result["map_background"] = self.map_background.to_dict()
        result["pitout_prediction"] = self.pitout_prediction.to_dict()
        result["pitout_prediction_while_requested_pitstop"] = self.pitout_prediction_while_requested_pitstop.to_dict()
        result["pitstop_duration"] = self.pitstop_duration.to_dict()
        result["player"] = self.player.to_dict()
        result["position_in_class"] = self.position_in_class.to_dict()
        result["proximity_circle"] = self.proximity_circle.to_dict()
        result["sector_line"] = self.sector_line.to_dict()
        result["start_line"] = self.start_line.to_dict()
        result["vehicle_standings"] = self.vehicle_standings.to_dict()
        result["fixed_pitstop_duration"] = self.fixed_pitstop_duration
        result["area_margin"] = self.area_margin
        result["area_size"] = self.area_size
        result["display_detail_level"] = self.display_detail_level
        result["display_orientation"] = self.display_orientation
        result["enable_multi_class_styling"] = self.enable_multi_class_styling
        result["enabled_fixed_pitout_prediction"] = self.enabled_fixed_pitout_prediction
        result["font_color"] = self.font_color
        result["map_color"] = self.map_color
        result["map_outline_color"] = self.map_outline_color
        result["map_outline_width"] = self.map_outline_width
        result["map_width"] = self.map_width
        result["number_of_prediction"] = self.number_of_prediction
        result["pitout_duration_increment"] = self.pitout_duration_increment
        result["pitout_duration_minimum"] = self.pitout_duration_minimum
        result["pitout_time_offset"] = self.pitout_time_offset
        result["prediction_outline_color"] = self.prediction_outline_color
        result["prediction_outline_width"] = self.prediction_outline_width
        result["proximity_circle_color"] = self.proximity_circle_color
        result["proximity_circle_radius"] = self.proximity_circle_radius
        result["proximity_circle_width"] = self.proximity_circle_width
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
        result["vehicle_outline_color"] = self.vehicle_outline_color
        result["vehicle_outline_color_laps_ahead"] = self.vehicle_outline_color_laps_ahead
        result["vehicle_outline_color_laps_behind"] = self.vehicle_outline_color_laps_behind
        result["vehicle_outline_player_color"] = self.vehicle_outline_player_color
        result["vehicle_outline_player_width"] = self.vehicle_outline_player_width
        result["vehicle_outline_width"] = self.vehicle_outline_width
        result["vehicle_outline_width_laps_ahead"] = self.vehicle_outline_width_laps_ahead
        result["vehicle_outline_width_laps_behind"] = self.vehicle_outline_width_laps_behind
        result["vehicle_scale"] = self.vehicle_scale
        result["vehicle_scale_player"] = self.vehicle_scale_player
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TrackMap":
        obj = cls()
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.bar_padding = data.get("bar_padding", obj.bar_padding)
        obj.font = FontConfig.from_dict(data.get("font", {}))
        obj.position = PositionConfig.from_dict(data.get("position", {}))
        obj.background = CellConfig.from_dict(data.get("background", {}), 'background')
        obj.custom_player_color_in_multi_class = CellConfig.from_dict(data.get("custom_player_color_in_multi_class", {}), 'custom_player_color_in_multi_class')
        obj.lap_difference_outline = CellConfig.from_dict(data.get("lap_difference_outline", {}), 'lap_difference_outline')
        obj.map = CellConfig.from_dict(data.get("map", {}), 'map')
        obj.map_background = CellConfig.from_dict(data.get("map_background", {}), 'map_background')
        obj.pitout_prediction = CellConfig.from_dict(data.get("pitout_prediction", {}), 'pitout_prediction')
        obj.pitout_prediction_while_requested_pitstop = CellConfig.from_dict(data.get("pitout_prediction_while_requested_pitstop", {}), 'pitout_prediction_while_requested_pitstop')
        obj.pitstop_duration = CellConfig.from_dict(data.get("pitstop_duration", {}), 'pitstop_duration')
        obj.player = CellConfig.from_dict(data.get("player", {}), 'player')
        obj.position_in_class = CellConfig.from_dict(data.get("position_in_class", {}), 'position_in_class')
        obj.proximity_circle = CellConfig.from_dict(data.get("proximity_circle", {}), 'proximity_circle')
        obj.sector_line = CellConfig.from_dict(data.get("sector_line", {}), 'sector_line')
        obj.start_line = CellConfig.from_dict(data.get("start_line", {}), 'start_line')
        obj.vehicle_standings = CellConfig.from_dict(data.get("vehicle_standings", {}), 'vehicle_standings')
        obj.fixed_pitstop_duration = data.get("fixed_pitstop_duration", obj.fixed_pitstop_duration)
        obj.area_margin = data.get("area_margin", obj.area_margin)
        obj.area_size = data.get("area_size", obj.area_size)
        obj.display_detail_level = data.get("display_detail_level", obj.display_detail_level)
        obj.display_orientation = data.get("display_orientation", obj.display_orientation)
        obj.enable_multi_class_styling = data.get("enable_multi_class_styling", obj.enable_multi_class_styling)
        obj.enabled_fixed_pitout_prediction = data.get("enabled_fixed_pitout_prediction", obj.enabled_fixed_pitout_prediction)
        obj.font_color = data.get("font_color", obj.font_color)
        obj.map_color = data.get("map_color", obj.map_color)
        obj.map_outline_color = data.get("map_outline_color", obj.map_outline_color)
        obj.map_outline_width = data.get("map_outline_width", obj.map_outline_width)
        obj.map_width = data.get("map_width", obj.map_width)
        obj.number_of_prediction = data.get("number_of_prediction", obj.number_of_prediction)
        obj.pitout_duration_increment = data.get("pitout_duration_increment", obj.pitout_duration_increment)
        obj.pitout_duration_minimum = data.get("pitout_duration_minimum", obj.pitout_duration_minimum)
        obj.pitout_time_offset = data.get("pitout_time_offset", obj.pitout_time_offset)
        obj.prediction_outline_color = data.get("prediction_outline_color", obj.prediction_outline_color)
        obj.prediction_outline_width = data.get("prediction_outline_width", obj.prediction_outline_width)
        obj.proximity_circle_color = data.get("proximity_circle_color", obj.proximity_circle_color)
        obj.proximity_circle_radius = data.get("proximity_circle_radius", obj.proximity_circle_radius)
        obj.proximity_circle_width = data.get("proximity_circle_width", obj.proximity_circle_width)
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
        obj.vehicle_outline_color = data.get("vehicle_outline_color", obj.vehicle_outline_color)
        obj.vehicle_outline_color_laps_ahead = data.get("vehicle_outline_color_laps_ahead", obj.vehicle_outline_color_laps_ahead)
        obj.vehicle_outline_color_laps_behind = data.get("vehicle_outline_color_laps_behind", obj.vehicle_outline_color_laps_behind)
        obj.vehicle_outline_player_color = data.get("vehicle_outline_player_color", obj.vehicle_outline_player_color)
        obj.vehicle_outline_player_width = data.get("vehicle_outline_player_width", obj.vehicle_outline_player_width)
        obj.vehicle_outline_width = data.get("vehicle_outline_width", obj.vehicle_outline_width)
        obj.vehicle_outline_width_laps_ahead = data.get("vehicle_outline_width_laps_ahead", obj.vehicle_outline_width_laps_ahead)
        obj.vehicle_outline_width_laps_behind = data.get("vehicle_outline_width_laps_behind", obj.vehicle_outline_width_laps_behind)
        obj.vehicle_scale = data.get("vehicle_scale", obj.vehicle_scale)
        obj.vehicle_scale_player = data.get("vehicle_scale_player", obj.vehicle_scale_player)
        return obj
