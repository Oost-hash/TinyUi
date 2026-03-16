# Auto-generated widget
# Widget: flag

from dataclasses import dataclass, field
from typing import Any, Dict

from ..base import CellConfig, FontConfig, PositionConfig, WidgetConfig
from ..colors import BRIGHT, DANGER, DARK_INVERT, GREEN, PIT, PLAYER, PLAYER_HIGHLIGHT, YELLOW_FLAG


@dataclass
class Flag(WidgetConfig):
    name: str = "flag"

    # groups
    font: FontConfig = field(default_factory=lambda: FontConfig(font_size=22))
    position: PositionConfig = field(default_factory=lambda: PositionConfig(position_x=556, position_y=509))

    # cells
    blue_flag: CellConfig = field(default_factory=lambda: CellConfig(id='blue_flag', font_color='#000000', bkg_color='#00AAFF', column_index=5))
    blue_flag_for_race_only: CellConfig = field(default_factory=lambda: CellConfig(id='blue_flag_for_race_only', show=False))
    disqualify: CellConfig = field(default_factory=lambda: CellConfig(id='disqualify', bkg_color='#000000'))
    finish: CellConfig = field(default_factory=lambda: CellConfig(id='finish', font_color=BRIGHT.font_color, bkg_color=BRIGHT.bkg_color))
    finish_state: CellConfig = field(default_factory=lambda: CellConfig(id='finish_state', column_index=9))
    green_flag: CellConfig = field(default_factory=lambda: CellConfig(id='green_flag', bkg_color='#00FF00'))
    low_fuel: CellConfig = field(default_factory=lambda: CellConfig(id='low_fuel', font_color='#000000', bkg_color='#EE7700', column_index=2))
    low_fuel_for_race_only: CellConfig = field(default_factory=lambda: CellConfig(id='low_fuel_for_race_only', show=False))
    pit_closed: CellConfig = field(default_factory=lambda: CellConfig(id='pit_closed', font_color=DANGER.font_color, bkg_color=DANGER.bkg_color))
    pit_request: CellConfig = field(default_factory=lambda: CellConfig(id='pit_request', font_color='#000000', bkg_color='#44AA00', column_index=8))
    pit_timer: CellConfig = field(default_factory=lambda: CellConfig(id='pit_timer', font_color='#000000', bkg_color='#22EE22', column_index=1))
    pit_timer_stopped: CellConfig = field(default_factory=lambda: CellConfig(id='pit_timer_stopped', font_color=PLAYER_HIGHLIGHT.font_color, bkg_color=PLAYER_HIGHLIGHT.bkg_color))
    red_lights: CellConfig = field(default_factory=lambda: CellConfig(id='red_lights', bkg_color='#FF2200'))
    speed_limiter: CellConfig = field(default_factory=lambda: CellConfig(id='speed_limiter', font_color=DANGER.font_color, bkg_color=DANGER.bkg_color, column_index=3))
    startlights: CellConfig = field(default_factory=lambda: CellConfig(id='startlights', font_color=DARK_INVERT.font_color, bkg_color=DARK_INVERT.bkg_color, column_index=6))
    traffic: CellConfig = field(default_factory=lambda: CellConfig(id='traffic', bkg_color='#4444FF', column_index=7))
    yellow_flag: CellConfig = field(default_factory=lambda: CellConfig(id='yellow_flag', font_color=YELLOW_FLAG.font_color, bkg_color=YELLOW_FLAG.bkg_color, column_index=4))
    yellow_flag_for_race_only: CellConfig = field(default_factory=lambda: CellConfig(id='yellow_flag_for_race_only', show=False))

    # config
    disqualify_text: str = 'DSQ'
    finish_text: str = 'FINISH'
    green_flag_duration: int = 3
    green_flag_text: str = 'GREEN'
    low_fuel_lap_threshold: int = 2
    low_fuel_volume_threshold: int = 20
    pit_closed_text: str = 'P CLOSE'
    pit_request_text: str = 'PIT REQ'
    pit_time_highlight_duration: int = 10
    red_lights_text: str = 'READY'
    speed_limiter_text: str = 'LIMITER'
    traffic_low_speed_threshold: int = 8
    traffic_maximum_time_gap: int = 15
    traffic_pitout_duration: int = 10
    yellow_flag_maximum_range_ahead: int = 500
    yellow_flag_maximum_range_behind: int = 50

    def to_flat(self) -> Dict[str, Any]:
        result = super().to_flat()
        result["name"] = self.name
        result.update(self.font.to_flat())
        result.update(self.position.to_flat())
        result.update(self.blue_flag.to_flat())
        result.update(self.blue_flag_for_race_only.to_flat())
        result.update(self.disqualify.to_flat())
        result.update(self.finish.to_flat())
        result.update(self.finish_state.to_flat())
        result.update(self.green_flag.to_flat())
        result.update(self.low_fuel.to_flat())
        result.update(self.low_fuel_for_race_only.to_flat())
        result.update(self.pit_closed.to_flat())
        result.update(self.pit_request.to_flat())
        result.update(self.pit_timer.to_flat())
        result.update(self.pit_timer_stopped.to_flat())
        result.update(self.red_lights.to_flat())
        result.update(self.speed_limiter.to_flat())
        result.update(self.startlights.to_flat())
        result.update(self.traffic.to_flat())
        result.update(self.yellow_flag.to_flat())
        result.update(self.yellow_flag_for_race_only.to_flat())
        result["disqualify_text"] = self.disqualify_text
        result["finish_text"] = self.finish_text
        result["green_flag_duration"] = self.green_flag_duration
        result["green_flag_text"] = self.green_flag_text
        result["low_fuel_lap_threshold"] = self.low_fuel_lap_threshold
        result["low_fuel_volume_threshold"] = self.low_fuel_volume_threshold
        result["pit_closed_text"] = self.pit_closed_text
        result["pit_request_text"] = self.pit_request_text
        result["pit_time_highlight_duration"] = self.pit_time_highlight_duration
        result["red_lights_text"] = self.red_lights_text
        result["speed_limiter_text"] = self.speed_limiter_text
        result["traffic_low_speed_threshold"] = self.traffic_low_speed_threshold
        result["traffic_maximum_time_gap"] = self.traffic_maximum_time_gap
        result["traffic_pitout_duration"] = self.traffic_pitout_duration
        result["yellow_flag_maximum_range_ahead"] = self.yellow_flag_maximum_range_ahead
        result["yellow_flag_maximum_range_behind"] = self.yellow_flag_maximum_range_behind
        return result

    @classmethod
    def from_flat(cls, data: Dict[str, Any]) -> "Flag":
        obj = cls()
        obj.name = data.get("name", obj.name)
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.font = FontConfig.from_flat(data)
        obj.position = PositionConfig.from_flat(data)
        obj.blue_flag = CellConfig.from_flat(data, 'blue_flag')
        obj.blue_flag_for_race_only = CellConfig.from_flat(data, 'blue_flag_for_race_only')
        obj.disqualify = CellConfig.from_flat(data, 'disqualify')
        obj.finish = CellConfig.from_flat(data, 'finish')
        obj.finish_state = CellConfig.from_flat(data, 'finish_state')
        obj.green_flag = CellConfig.from_flat(data, 'green_flag')
        obj.low_fuel = CellConfig.from_flat(data, 'low_fuel')
        obj.low_fuel_for_race_only = CellConfig.from_flat(data, 'low_fuel_for_race_only')
        obj.pit_closed = CellConfig.from_flat(data, 'pit_closed')
        obj.pit_request = CellConfig.from_flat(data, 'pit_request')
        obj.pit_timer = CellConfig.from_flat(data, 'pit_timer')
        obj.pit_timer_stopped = CellConfig.from_flat(data, 'pit_timer_stopped')
        obj.red_lights = CellConfig.from_flat(data, 'red_lights')
        obj.speed_limiter = CellConfig.from_flat(data, 'speed_limiter')
        obj.startlights = CellConfig.from_flat(data, 'startlights')
        obj.traffic = CellConfig.from_flat(data, 'traffic')
        obj.yellow_flag = CellConfig.from_flat(data, 'yellow_flag')
        obj.yellow_flag_for_race_only = CellConfig.from_flat(data, 'yellow_flag_for_race_only')
        obj.disqualify_text = data.get("disqualify_text", obj.disqualify_text)
        obj.finish_text = data.get("finish_text", obj.finish_text)
        obj.green_flag_duration = data.get("green_flag_duration", obj.green_flag_duration)
        obj.green_flag_text = data.get("green_flag_text", obj.green_flag_text)
        obj.low_fuel_lap_threshold = data.get("low_fuel_lap_threshold", obj.low_fuel_lap_threshold)
        obj.low_fuel_volume_threshold = data.get("low_fuel_volume_threshold", obj.low_fuel_volume_threshold)
        obj.pit_closed_text = data.get("pit_closed_text", obj.pit_closed_text)
        obj.pit_request_text = data.get("pit_request_text", obj.pit_request_text)
        obj.pit_time_highlight_duration = data.get("pit_time_highlight_duration", obj.pit_time_highlight_duration)
        obj.red_lights_text = data.get("red_lights_text", obj.red_lights_text)
        obj.speed_limiter_text = data.get("speed_limiter_text", obj.speed_limiter_text)
        obj.traffic_low_speed_threshold = data.get("traffic_low_speed_threshold", obj.traffic_low_speed_threshold)
        obj.traffic_maximum_time_gap = data.get("traffic_maximum_time_gap", obj.traffic_maximum_time_gap)
        obj.traffic_pitout_duration = data.get("traffic_pitout_duration", obj.traffic_pitout_duration)
        obj.yellow_flag_maximum_range_ahead = data.get("yellow_flag_maximum_range_ahead", obj.yellow_flag_maximum_range_ahead)
        obj.yellow_flag_maximum_range_behind = data.get("yellow_flag_maximum_range_behind", obj.yellow_flag_maximum_range_behind)
        return obj

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["font"] = self.font.to_dict()
        result["position"] = self.position.to_dict()
        result["blue_flag"] = self.blue_flag.to_dict()
        result["blue_flag_for_race_only"] = self.blue_flag_for_race_only.to_dict()
        result["disqualify"] = self.disqualify.to_dict()
        result["finish"] = self.finish.to_dict()
        result["finish_state"] = self.finish_state.to_dict()
        result["green_flag"] = self.green_flag.to_dict()
        result["low_fuel"] = self.low_fuel.to_dict()
        result["low_fuel_for_race_only"] = self.low_fuel_for_race_only.to_dict()
        result["pit_closed"] = self.pit_closed.to_dict()
        result["pit_request"] = self.pit_request.to_dict()
        result["pit_timer"] = self.pit_timer.to_dict()
        result["pit_timer_stopped"] = self.pit_timer_stopped.to_dict()
        result["red_lights"] = self.red_lights.to_dict()
        result["speed_limiter"] = self.speed_limiter.to_dict()
        result["startlights"] = self.startlights.to_dict()
        result["traffic"] = self.traffic.to_dict()
        result["yellow_flag"] = self.yellow_flag.to_dict()
        result["yellow_flag_for_race_only"] = self.yellow_flag_for_race_only.to_dict()
        result["disqualify_text"] = self.disqualify_text
        result["finish_text"] = self.finish_text
        result["green_flag_duration"] = self.green_flag_duration
        result["green_flag_text"] = self.green_flag_text
        result["low_fuel_lap_threshold"] = self.low_fuel_lap_threshold
        result["low_fuel_volume_threshold"] = self.low_fuel_volume_threshold
        result["pit_closed_text"] = self.pit_closed_text
        result["pit_request_text"] = self.pit_request_text
        result["pit_time_highlight_duration"] = self.pit_time_highlight_duration
        result["red_lights_text"] = self.red_lights_text
        result["speed_limiter_text"] = self.speed_limiter_text
        result["traffic_low_speed_threshold"] = self.traffic_low_speed_threshold
        result["traffic_maximum_time_gap"] = self.traffic_maximum_time_gap
        result["traffic_pitout_duration"] = self.traffic_pitout_duration
        result["yellow_flag_maximum_range_ahead"] = self.yellow_flag_maximum_range_ahead
        result["yellow_flag_maximum_range_behind"] = self.yellow_flag_maximum_range_behind
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Flag":
        obj = cls()
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.font = FontConfig.from_dict(data.get("font", {}))
        obj.position = PositionConfig.from_dict(data.get("position", {}))
        obj.blue_flag = CellConfig.from_dict(data.get("blue_flag", {}), 'blue_flag')
        obj.blue_flag_for_race_only = CellConfig.from_dict(data.get("blue_flag_for_race_only", {}), 'blue_flag_for_race_only')
        obj.disqualify = CellConfig.from_dict(data.get("disqualify", {}), 'disqualify')
        obj.finish = CellConfig.from_dict(data.get("finish", {}), 'finish')
        obj.finish_state = CellConfig.from_dict(data.get("finish_state", {}), 'finish_state')
        obj.green_flag = CellConfig.from_dict(data.get("green_flag", {}), 'green_flag')
        obj.low_fuel = CellConfig.from_dict(data.get("low_fuel", {}), 'low_fuel')
        obj.low_fuel_for_race_only = CellConfig.from_dict(data.get("low_fuel_for_race_only", {}), 'low_fuel_for_race_only')
        obj.pit_closed = CellConfig.from_dict(data.get("pit_closed", {}), 'pit_closed')
        obj.pit_request = CellConfig.from_dict(data.get("pit_request", {}), 'pit_request')
        obj.pit_timer = CellConfig.from_dict(data.get("pit_timer", {}), 'pit_timer')
        obj.pit_timer_stopped = CellConfig.from_dict(data.get("pit_timer_stopped", {}), 'pit_timer_stopped')
        obj.red_lights = CellConfig.from_dict(data.get("red_lights", {}), 'red_lights')
        obj.speed_limiter = CellConfig.from_dict(data.get("speed_limiter", {}), 'speed_limiter')
        obj.startlights = CellConfig.from_dict(data.get("startlights", {}), 'startlights')
        obj.traffic = CellConfig.from_dict(data.get("traffic", {}), 'traffic')
        obj.yellow_flag = CellConfig.from_dict(data.get("yellow_flag", {}), 'yellow_flag')
        obj.yellow_flag_for_race_only = CellConfig.from_dict(data.get("yellow_flag_for_race_only", {}), 'yellow_flag_for_race_only')
        obj.disqualify_text = data.get("disqualify_text", obj.disqualify_text)
        obj.finish_text = data.get("finish_text", obj.finish_text)
        obj.green_flag_duration = data.get("green_flag_duration", obj.green_flag_duration)
        obj.green_flag_text = data.get("green_flag_text", obj.green_flag_text)
        obj.low_fuel_lap_threshold = data.get("low_fuel_lap_threshold", obj.low_fuel_lap_threshold)
        obj.low_fuel_volume_threshold = data.get("low_fuel_volume_threshold", obj.low_fuel_volume_threshold)
        obj.pit_closed_text = data.get("pit_closed_text", obj.pit_closed_text)
        obj.pit_request_text = data.get("pit_request_text", obj.pit_request_text)
        obj.pit_time_highlight_duration = data.get("pit_time_highlight_duration", obj.pit_time_highlight_duration)
        obj.red_lights_text = data.get("red_lights_text", obj.red_lights_text)
        obj.speed_limiter_text = data.get("speed_limiter_text", obj.speed_limiter_text)
        obj.traffic_low_speed_threshold = data.get("traffic_low_speed_threshold", obj.traffic_low_speed_threshold)
        obj.traffic_maximum_time_gap = data.get("traffic_maximum_time_gap", obj.traffic_maximum_time_gap)
        obj.traffic_pitout_duration = data.get("traffic_pitout_duration", obj.traffic_pitout_duration)
        obj.yellow_flag_maximum_range_ahead = data.get("yellow_flag_maximum_range_ahead", obj.yellow_flag_maximum_range_ahead)
        obj.yellow_flag_maximum_range_behind = data.get("yellow_flag_maximum_range_behind", obj.yellow_flag_maximum_range_behind)
        return obj
