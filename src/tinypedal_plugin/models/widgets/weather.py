# Auto-generated widget
# Widget: weather

from dataclasses import dataclass, field
from typing import Any, Dict

from ..base import CellConfig, FontConfig, PositionConfig, WidgetConfig
from ..colors import BRIGHT, BRIGHT_GREEN, GREEN, READING


@dataclass
class Weather(WidgetConfig):
    name: str = "weather"

    # base overrides
    update_interval: int = 100

    # groups
    font: FontConfig = field(default_factory=FontConfig)
    position: PositionConfig = field(default_factory=lambda: PositionConfig(position_x=57, position_y=70))

    # cells
    dry: CellConfig = field(default_factory=lambda: CellConfig(id='dry', prefix='Dry'))
    rain: CellConfig = field(default_factory=lambda: CellConfig(id='rain', prefix='Rain', column_index=2))
    rubber_coverage_while_dry: CellConfig = field(default_factory=lambda: CellConfig(id='rubber_coverage_while_dry'))
    temperature: CellConfig = field(default_factory=lambda: CellConfig(id='temperature', decimal_places=1, column_index=1))
    trend_constant: CellConfig = field(default_factory=lambda: CellConfig(id='trend_constant', font_color=READING.font_color, bkg_color=READING.bkg_color))
    trend_decreasing: CellConfig = field(default_factory=lambda: CellConfig(id='trend_decreasing', font_color=BRIGHT_GREEN.font_color, bkg_color=BRIGHT_GREEN.bkg_color))
    trend_increasing: CellConfig = field(default_factory=lambda: CellConfig(id='trend_increasing', font_color='#FF4400'))
    wet: CellConfig = field(default_factory=lambda: CellConfig(id='wet', prefix='Wet'))
    wetness: CellConfig = field(default_factory=lambda: CellConfig(id='wetness', column_index=3))

    # config
    raininess_trend_interval: int = 60
    rubber_median_laps: int = 2000
    rubber_time_scale_practice: int = 1
    rubber_time_scale_qualifying: int = 1
    rubber_time_scale_race: int = 1
    starting_rubber_practice: float = 0.25
    starting_rubber_qualifying: float = 0.5
    starting_rubber_race: float = 0.5
    temperature_trend_interval: int = 60
    wetness_trend_interval: int = 60

    def to_flat(self) -> Dict[str, Any]:
        result = super().to_flat()
        result["name"] = self.name
        result["update_interval"] = self.update_interval
        result.update(self.font.to_flat())
        result.update(self.position.to_flat())
        result.update(self.dry.to_flat())
        result.update(self.rain.to_flat())
        result.update(self.rubber_coverage_while_dry.to_flat())
        result.update(self.temperature.to_flat())
        result.update(self.trend_constant.to_flat())
        result.update(self.trend_decreasing.to_flat())
        result.update(self.trend_increasing.to_flat())
        result.update(self.wet.to_flat())
        result.update(self.wetness.to_flat())
        result["raininess_trend_interval"] = self.raininess_trend_interval
        result["rubber_median_laps"] = self.rubber_median_laps
        result["rubber_time_scale_practice"] = self.rubber_time_scale_practice
        result["rubber_time_scale_qualifying"] = self.rubber_time_scale_qualifying
        result["rubber_time_scale_race"] = self.rubber_time_scale_race
        result["starting_rubber_practice"] = self.starting_rubber_practice
        result["starting_rubber_qualifying"] = self.starting_rubber_qualifying
        result["starting_rubber_race"] = self.starting_rubber_race
        result["temperature_trend_interval"] = self.temperature_trend_interval
        result["wetness_trend_interval"] = self.wetness_trend_interval
        return result

    @classmethod
    def from_flat(cls, data: Dict[str, Any]) -> "Weather":
        obj = cls()
        obj.name = data.get("name", obj.name)
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.update_interval = data.get("update_interval", obj.update_interval)
        obj.font = FontConfig.from_flat(data)
        obj.position = PositionConfig.from_flat(data)
        obj.dry = CellConfig.from_flat(data, 'dry')
        obj.rain = CellConfig.from_flat(data, 'rain')
        obj.rubber_coverage_while_dry = CellConfig.from_flat(data, 'rubber_coverage_while_dry')
        obj.temperature = CellConfig.from_flat(data, 'temperature')
        obj.trend_constant = CellConfig.from_flat(data, 'trend_constant')
        obj.trend_decreasing = CellConfig.from_flat(data, 'trend_decreasing')
        obj.trend_increasing = CellConfig.from_flat(data, 'trend_increasing')
        obj.wet = CellConfig.from_flat(data, 'wet')
        obj.wetness = CellConfig.from_flat(data, 'wetness')
        obj.raininess_trend_interval = data.get("raininess_trend_interval", obj.raininess_trend_interval)
        obj.rubber_median_laps = data.get("rubber_median_laps", obj.rubber_median_laps)
        obj.rubber_time_scale_practice = data.get("rubber_time_scale_practice", obj.rubber_time_scale_practice)
        obj.rubber_time_scale_qualifying = data.get("rubber_time_scale_qualifying", obj.rubber_time_scale_qualifying)
        obj.rubber_time_scale_race = data.get("rubber_time_scale_race", obj.rubber_time_scale_race)
        obj.starting_rubber_practice = data.get("starting_rubber_practice", obj.starting_rubber_practice)
        obj.starting_rubber_qualifying = data.get("starting_rubber_qualifying", obj.starting_rubber_qualifying)
        obj.starting_rubber_race = data.get("starting_rubber_race", obj.starting_rubber_race)
        obj.temperature_trend_interval = data.get("temperature_trend_interval", obj.temperature_trend_interval)
        obj.wetness_trend_interval = data.get("wetness_trend_interval", obj.wetness_trend_interval)
        return obj

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["update_interval"] = self.update_interval
        result["font"] = self.font.to_dict()
        result["position"] = self.position.to_dict()
        result["dry"] = self.dry.to_dict()
        result["rain"] = self.rain.to_dict()
        result["rubber_coverage_while_dry"] = self.rubber_coverage_while_dry.to_dict()
        result["temperature"] = self.temperature.to_dict()
        result["trend_constant"] = self.trend_constant.to_dict()
        result["trend_decreasing"] = self.trend_decreasing.to_dict()
        result["trend_increasing"] = self.trend_increasing.to_dict()
        result["wet"] = self.wet.to_dict()
        result["wetness"] = self.wetness.to_dict()
        result["raininess_trend_interval"] = self.raininess_trend_interval
        result["rubber_median_laps"] = self.rubber_median_laps
        result["rubber_time_scale_practice"] = self.rubber_time_scale_practice
        result["rubber_time_scale_qualifying"] = self.rubber_time_scale_qualifying
        result["rubber_time_scale_race"] = self.rubber_time_scale_race
        result["starting_rubber_practice"] = self.starting_rubber_practice
        result["starting_rubber_qualifying"] = self.starting_rubber_qualifying
        result["starting_rubber_race"] = self.starting_rubber_race
        result["temperature_trend_interval"] = self.temperature_trend_interval
        result["wetness_trend_interval"] = self.wetness_trend_interval
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Weather":
        obj = cls()
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.update_interval = data.get("update_interval", obj.update_interval)
        obj.font = FontConfig.from_dict(data.get("font", {}))
        obj.position = PositionConfig.from_dict(data.get("position", {}))
        obj.dry = CellConfig.from_dict(data.get("dry", {}), 'dry')
        obj.rain = CellConfig.from_dict(data.get("rain", {}), 'rain')
        obj.rubber_coverage_while_dry = CellConfig.from_dict(data.get("rubber_coverage_while_dry", {}), 'rubber_coverage_while_dry')
        obj.temperature = CellConfig.from_dict(data.get("temperature", {}), 'temperature')
        obj.trend_constant = CellConfig.from_dict(data.get("trend_constant", {}), 'trend_constant')
        obj.trend_decreasing = CellConfig.from_dict(data.get("trend_decreasing", {}), 'trend_decreasing')
        obj.trend_increasing = CellConfig.from_dict(data.get("trend_increasing", {}), 'trend_increasing')
        obj.wet = CellConfig.from_dict(data.get("wet", {}), 'wet')
        obj.wetness = CellConfig.from_dict(data.get("wetness", {}), 'wetness')
        obj.raininess_trend_interval = data.get("raininess_trend_interval", obj.raininess_trend_interval)
        obj.rubber_median_laps = data.get("rubber_median_laps", obj.rubber_median_laps)
        obj.rubber_time_scale_practice = data.get("rubber_time_scale_practice", obj.rubber_time_scale_practice)
        obj.rubber_time_scale_qualifying = data.get("rubber_time_scale_qualifying", obj.rubber_time_scale_qualifying)
        obj.rubber_time_scale_race = data.get("rubber_time_scale_race", obj.rubber_time_scale_race)
        obj.starting_rubber_practice = data.get("starting_rubber_practice", obj.starting_rubber_practice)
        obj.starting_rubber_qualifying = data.get("starting_rubber_qualifying", obj.starting_rubber_qualifying)
        obj.starting_rubber_race = data.get("starting_rubber_race", obj.starting_rubber_race)
        obj.temperature_trend_interval = data.get("temperature_trend_interval", obj.temperature_trend_interval)
        obj.wetness_trend_interval = data.get("wetness_trend_interval", obj.wetness_trend_interval)
        return obj
