# Auto-generated widget
# Widget: track_clock

from dataclasses import dataclass, field
from typing import Any, Dict

from ..base import CellConfig, FontConfig, PositionConfig, WidgetConfig
from ..colors import AMBER


@dataclass
class TrackClock(WidgetConfig):
    name: str = "track_clock"

    # base overrides
    layout: int = 1
    update_interval: int = 200

    # groups
    font: FontConfig = field(default_factory=FontConfig)
    position: PositionConfig = field(default_factory=lambda: PositionConfig(position_x=340, position_y=42))

    # cells
    phase_day: CellConfig = field(default_factory=lambda: CellConfig(id='phase_day', font_color=AMBER.font_color, bkg_color=AMBER.bkg_color))
    phase_night: CellConfig = field(default_factory=lambda: CellConfig(id='phase_night', font_color='#00AAFF'))
    sunlight_phase_countdown: CellConfig = field(default_factory=lambda: CellConfig(id='sunlight_phase_countdown', column_index=3))
    time_scale: CellConfig = field(default_factory=lambda: CellConfig(id='time_scale', prefix='X', column_index=2))
    track_clock: CellConfig = field(default_factory=lambda: CellConfig(id='track_clock', column_index=1))

    # config
    enable_time_scaled_countdown: bool = False
    enable_track_clock_synchronization: bool = True
    track_clock_format: str = '%H:%M%p'
    track_clock_time_scale: int = 1

    def to_flat(self) -> Dict[str, Any]:
        result = super().to_flat()
        result["name"] = self.name
        result["layout"] = self.layout
        result["update_interval"] = self.update_interval
        result.update(self.font.to_flat())
        result.update(self.position.to_flat())
        result.update(self.phase_day.to_flat())
        result.update(self.phase_night.to_flat())
        result.update(self.sunlight_phase_countdown.to_flat())
        result.update(self.time_scale.to_flat())
        result.update(self.track_clock.to_flat())
        result["enable_time_scaled_countdown"] = self.enable_time_scaled_countdown
        result["enable_track_clock_synchronization"] = self.enable_track_clock_synchronization
        result["track_clock_format"] = self.track_clock_format
        result["track_clock_time_scale"] = self.track_clock_time_scale
        return result

    @classmethod
    def from_flat(cls, data: Dict[str, Any]) -> "TrackClock":
        obj = cls()
        obj.name = data.get("name", obj.name)
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.layout = data.get("layout", obj.layout)
        obj.update_interval = data.get("update_interval", obj.update_interval)
        obj.font = FontConfig.from_flat(data)
        obj.position = PositionConfig.from_flat(data)
        obj.phase_day = CellConfig.from_flat(data, 'phase_day')
        obj.phase_night = CellConfig.from_flat(data, 'phase_night')
        obj.sunlight_phase_countdown = CellConfig.from_flat(data, 'sunlight_phase_countdown')
        obj.time_scale = CellConfig.from_flat(data, 'time_scale')
        obj.track_clock = CellConfig.from_flat(data, 'track_clock')
        obj.enable_time_scaled_countdown = data.get("enable_time_scaled_countdown", obj.enable_time_scaled_countdown)
        obj.enable_track_clock_synchronization = data.get("enable_track_clock_synchronization", obj.enable_track_clock_synchronization)
        obj.track_clock_format = data.get("track_clock_format", obj.track_clock_format)
        obj.track_clock_time_scale = data.get("track_clock_time_scale", obj.track_clock_time_scale)
        return obj

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["layout"] = self.layout
        result["update_interval"] = self.update_interval
        result["font"] = self.font.to_dict()
        result["position"] = self.position.to_dict()
        result["phase_day"] = self.phase_day.to_dict()
        result["phase_night"] = self.phase_night.to_dict()
        result["sunlight_phase_countdown"] = self.sunlight_phase_countdown.to_dict()
        result["time_scale"] = self.time_scale.to_dict()
        result["track_clock"] = self.track_clock.to_dict()
        result["enable_time_scaled_countdown"] = self.enable_time_scaled_countdown
        result["enable_track_clock_synchronization"] = self.enable_track_clock_synchronization
        result["track_clock_format"] = self.track_clock_format
        result["track_clock_time_scale"] = self.track_clock_time_scale
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TrackClock":
        obj = cls()
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.layout = data.get("layout", obj.layout)
        obj.update_interval = data.get("update_interval", obj.update_interval)
        obj.font = FontConfig.from_dict(data.get("font", {}))
        obj.position = PositionConfig.from_dict(data.get("position", {}))
        obj.phase_day = CellConfig.from_dict(data.get("phase_day", {}), 'phase_day')
        obj.phase_night = CellConfig.from_dict(data.get("phase_night", {}), 'phase_night')
        obj.sunlight_phase_countdown = CellConfig.from_dict(data.get("sunlight_phase_countdown", {}), 'sunlight_phase_countdown')
        obj.time_scale = CellConfig.from_dict(data.get("time_scale", {}), 'time_scale')
        obj.track_clock = CellConfig.from_dict(data.get("track_clock", {}), 'track_clock')
        obj.enable_time_scaled_countdown = data.get("enable_time_scaled_countdown", obj.enable_time_scaled_countdown)
        obj.enable_track_clock_synchronization = data.get("enable_track_clock_synchronization", obj.enable_track_clock_synchronization)
        obj.track_clock_format = data.get("track_clock_format", obj.track_clock_format)
        obj.track_clock_time_scale = data.get("track_clock_time_scale", obj.track_clock_time_scale)
        return obj
