# Auto-generated widget
# Widget: tyre_pressure

from dataclasses import dataclass, field
from typing import Any, Dict

from ..base import BarConfig, CellConfig, FontConfig, PositionConfig, WidgetConfig
from ..colors import COMPOUND, LIGHT_BLUE, ORANGE, READING


@dataclass
class TyrePressure(WidgetConfig):
    name: str = "tyre_pressure"

    # groups
    bar: BarConfig = field(default_factory=BarConfig)
    font: FontConfig = field(default_factory=FontConfig)
    position: PositionConfig = field(default_factory=lambda: PositionConfig(position_x=57, position_y=383))

    # cells
    pressure: CellConfig = field(default_factory=lambda: CellConfig(id='pressure', column_index=1))
    pressure_cold: CellConfig = field(default_factory=lambda: CellConfig(id='pressure_cold', font_color=LIGHT_BLUE.font_color, bkg_color=LIGHT_BLUE.bkg_color))
    pressure_deviation: CellConfig = field(default_factory=lambda: CellConfig(id='pressure_deviation', font_color=READING.font_color, bkg_color=READING.bkg_color, column_index=2))
    pressure_hot: CellConfig = field(default_factory=lambda: CellConfig(id='pressure_hot', font_color=ORANGE.font_color, bkg_color=ORANGE.bkg_color))
    tyre_compound: CellConfig = field(default_factory=lambda: CellConfig(id='tyre_compound', font_color=COMPOUND.font_color, bkg_color=COMPOUND.bkg_color))

    # config
    average_sampling_duration: int = 10
    hot_pressure_temperature_threshold: int = 65
    swap_style: bool = False

    def to_flat(self) -> Dict[str, Any]:
        result = super().to_flat()
        result["name"] = self.name
        result.update(self.bar.to_flat())
        result.update(self.font.to_flat())
        result.update(self.position.to_flat())
        result.update(self.pressure.to_flat())
        result.update(self.pressure_cold.to_flat())
        result.update(self.pressure_deviation.to_flat())
        result.update(self.pressure_hot.to_flat())
        result.update(self.tyre_compound.to_flat())
        result["average_sampling_duration"] = self.average_sampling_duration
        result["hot_pressure_temperature_threshold"] = self.hot_pressure_temperature_threshold
        result["swap_style"] = self.swap_style
        return result

    @classmethod
    def from_flat(cls, data: Dict[str, Any]) -> "TyrePressure":
        obj = cls()
        obj.name = data.get("name", obj.name)
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.bar = BarConfig.from_flat(data)
        obj.font = FontConfig.from_flat(data)
        obj.position = PositionConfig.from_flat(data)
        obj.pressure = CellConfig.from_flat(data, 'pressure')
        obj.pressure_cold = CellConfig.from_flat(data, 'pressure_cold')
        obj.pressure_deviation = CellConfig.from_flat(data, 'pressure_deviation')
        obj.pressure_hot = CellConfig.from_flat(data, 'pressure_hot')
        obj.tyre_compound = CellConfig.from_flat(data, 'tyre_compound')
        obj.average_sampling_duration = data.get("average_sampling_duration", obj.average_sampling_duration)
        obj.hot_pressure_temperature_threshold = data.get("hot_pressure_temperature_threshold", obj.hot_pressure_temperature_threshold)
        obj.swap_style = data.get("swap_style", obj.swap_style)
        return obj

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["bar"] = self.bar.to_dict()
        result["font"] = self.font.to_dict()
        result["position"] = self.position.to_dict()
        result["pressure"] = self.pressure.to_dict()
        result["pressure_cold"] = self.pressure_cold.to_dict()
        result["pressure_deviation"] = self.pressure_deviation.to_dict()
        result["pressure_hot"] = self.pressure_hot.to_dict()
        result["tyre_compound"] = self.tyre_compound.to_dict()
        result["average_sampling_duration"] = self.average_sampling_duration
        result["hot_pressure_temperature_threshold"] = self.hot_pressure_temperature_threshold
        result["swap_style"] = self.swap_style
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TyrePressure":
        obj = cls()
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.bar = BarConfig.from_dict(data.get("bar", {}))
        obj.font = FontConfig.from_dict(data.get("font", {}))
        obj.position = PositionConfig.from_dict(data.get("position", {}))
        obj.pressure = CellConfig.from_dict(data.get("pressure", {}), 'pressure')
        obj.pressure_cold = CellConfig.from_dict(data.get("pressure_cold", {}), 'pressure_cold')
        obj.pressure_deviation = CellConfig.from_dict(data.get("pressure_deviation", {}), 'pressure_deviation')
        obj.pressure_hot = CellConfig.from_dict(data.get("pressure_hot", {}), 'pressure_hot')
        obj.tyre_compound = CellConfig.from_dict(data.get("tyre_compound", {}), 'tyre_compound')
        obj.average_sampling_duration = data.get("average_sampling_duration", obj.average_sampling_duration)
        obj.hot_pressure_temperature_threshold = data.get("hot_pressure_temperature_threshold", obj.hot_pressure_temperature_threshold)
        obj.swap_style = data.get("swap_style", obj.swap_style)
        return obj
