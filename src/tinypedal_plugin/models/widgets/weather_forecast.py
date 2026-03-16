# Auto-generated widget
# Widget: weather_forecast

from dataclasses import dataclass, field
from typing import Any, Dict

from ..base import CellConfig, FontConfig, PositionConfig, WidgetConfig
from ..colors import BRIGHT


@dataclass
class WeatherForecast(WidgetConfig):
    name: str = "weather_forecast"

    # base overrides
    update_interval: int = 100

    # groups
    font: FontConfig = field(default_factory=lambda: FontConfig(font_size=11))
    position: PositionConfig = field(default_factory=lambda: PositionConfig(position_x=256, position_y=640))

    # cells
    ambient_temperature: CellConfig = field(default_factory=lambda: CellConfig(id='ambient_temperature', font_color=BRIGHT.font_color, bkg_color=BRIGHT.bkg_color, column_index=3))
    estimated_time: CellConfig = field(default_factory=lambda: CellConfig(id='estimated_time', font_color=BRIGHT.font_color, bkg_color=BRIGHT.bkg_color, column_index=1))
    rain_chance_bar: CellConfig = field(default_factory=lambda: CellConfig(id='rain_chance_bar', column_index=4))
    unavailable_data: CellConfig = field(default_factory=lambda: CellConfig(id='unavailable_data', show=False))
    weather_icon: CellConfig = field(default_factory=lambda: CellConfig(id='weather_icon', column_index=2))

    # config
    icon_size: int = 32
    number_of_forecasts: int = 4
    rain_chance_bar_bkg_color: str = '#88222222'
    rain_chance_bar_color: str = '#FF00FF'
    rain_chance_bar_height: int = 5

    def to_flat(self) -> Dict[str, Any]:
        result = super().to_flat()
        result["name"] = self.name
        result["update_interval"] = self.update_interval
        result.update(self.font.to_flat())
        result.update(self.position.to_flat())
        result.update(self.ambient_temperature.to_flat())
        result.update(self.estimated_time.to_flat())
        result.update(self.rain_chance_bar.to_flat())
        result.update(self.unavailable_data.to_flat())
        result.update(self.weather_icon.to_flat())
        result["icon_size"] = self.icon_size
        result["number_of_forecasts"] = self.number_of_forecasts
        result["rain_chance_bar_bkg_color"] = self.rain_chance_bar_bkg_color
        result["rain_chance_bar_color"] = self.rain_chance_bar_color
        result["rain_chance_bar_height"] = self.rain_chance_bar_height
        return result

    @classmethod
    def from_flat(cls, data: Dict[str, Any]) -> "WeatherForecast":
        obj = cls()
        obj.name = data.get("name", obj.name)
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.update_interval = data.get("update_interval", obj.update_interval)
        obj.font = FontConfig.from_flat(data)
        obj.position = PositionConfig.from_flat(data)
        obj.ambient_temperature = CellConfig.from_flat(data, 'ambient_temperature')
        obj.estimated_time = CellConfig.from_flat(data, 'estimated_time')
        obj.rain_chance_bar = CellConfig.from_flat(data, 'rain_chance_bar')
        obj.unavailable_data = CellConfig.from_flat(data, 'unavailable_data')
        obj.weather_icon = CellConfig.from_flat(data, 'weather_icon')
        obj.icon_size = data.get("icon_size", obj.icon_size)
        obj.number_of_forecasts = data.get("number_of_forecasts", obj.number_of_forecasts)
        obj.rain_chance_bar_bkg_color = data.get("rain_chance_bar_bkg_color", obj.rain_chance_bar_bkg_color)
        obj.rain_chance_bar_color = data.get("rain_chance_bar_color", obj.rain_chance_bar_color)
        obj.rain_chance_bar_height = data.get("rain_chance_bar_height", obj.rain_chance_bar_height)
        return obj

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["update_interval"] = self.update_interval
        result["font"] = self.font.to_dict()
        result["position"] = self.position.to_dict()
        result["ambient_temperature"] = self.ambient_temperature.to_dict()
        result["estimated_time"] = self.estimated_time.to_dict()
        result["rain_chance_bar"] = self.rain_chance_bar.to_dict()
        result["unavailable_data"] = self.unavailable_data.to_dict()
        result["weather_icon"] = self.weather_icon.to_dict()
        result["icon_size"] = self.icon_size
        result["number_of_forecasts"] = self.number_of_forecasts
        result["rain_chance_bar_bkg_color"] = self.rain_chance_bar_bkg_color
        result["rain_chance_bar_color"] = self.rain_chance_bar_color
        result["rain_chance_bar_height"] = self.rain_chance_bar_height
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WeatherForecast":
        obj = cls()
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.update_interval = data.get("update_interval", obj.update_interval)
        obj.font = FontConfig.from_dict(data.get("font", {}))
        obj.position = PositionConfig.from_dict(data.get("position", {}))
        obj.ambient_temperature = CellConfig.from_dict(data.get("ambient_temperature", {}), 'ambient_temperature')
        obj.estimated_time = CellConfig.from_dict(data.get("estimated_time", {}), 'estimated_time')
        obj.rain_chance_bar = CellConfig.from_dict(data.get("rain_chance_bar", {}), 'rain_chance_bar')
        obj.unavailable_data = CellConfig.from_dict(data.get("unavailable_data", {}), 'unavailable_data')
        obj.weather_icon = CellConfig.from_dict(data.get("weather_icon", {}), 'weather_icon')
        obj.icon_size = data.get("icon_size", obj.icon_size)
        obj.number_of_forecasts = data.get("number_of_forecasts", obj.number_of_forecasts)
        obj.rain_chance_bar_bkg_color = data.get("rain_chance_bar_bkg_color", obj.rain_chance_bar_bkg_color)
        obj.rain_chance_bar_color = data.get("rain_chance_bar_color", obj.rain_chance_bar_color)
        obj.rain_chance_bar_height = data.get("rain_chance_bar_height", obj.rain_chance_bar_height)
        return obj
