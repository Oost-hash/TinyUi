# Auto-generated widget
# Widget: brake_temperature

from dataclasses import dataclass, field
from typing import Any, Dict

from ..base import BarConfig, CellConfig, FontConfig, PositionConfig, WidgetConfig
from ..colors import DARK_INVERT, DEFAULT, READING


@dataclass
class BrakeTemperature(WidgetConfig):
    name: str = "brake_temperature"

    # groups
    bar: BarConfig = field(default_factory=BarConfig)
    font: FontConfig = field(default_factory=FontConfig)
    position: PositionConfig = field(default_factory=lambda: PositionConfig(position_x=460, position_y=525))

    # cells
    average: CellConfig = field(default_factory=lambda: CellConfig(id='average', font_color=READING.font_color, bkg_color=READING.bkg_color, column_index=2))
    degree_sign: CellConfig = field(default_factory=lambda: CellConfig(id='degree_sign', show=False))
    temperature: CellConfig = field(default_factory=lambda: CellConfig(id='temperature', font_color=DARK_INVERT.font_color, bkg_color=DARK_INVERT.bkg_color, column_index=1))

    # config
    average_sampling_duration: int = 10
    enable_heatmap_auto_matching: bool = True
    heatmap_name: str = 'HEATMAP_DEFAULT_BRAKE'
    leading_zero: int = 2
    off_brake_duration: int = 1
    swap_style: bool = False

    def to_flat(self) -> Dict[str, Any]:
        result = super().to_flat()
        result["name"] = self.name
        result.update(self.bar.to_flat())
        result.update(self.font.to_flat())
        result.update(self.position.to_flat())
        result.update(self.average.to_flat())
        result.update(self.degree_sign.to_flat())
        result.update(self.temperature.to_flat())
        result["average_sampling_duration"] = self.average_sampling_duration
        result["enable_heatmap_auto_matching"] = self.enable_heatmap_auto_matching
        result["heatmap_name"] = self.heatmap_name
        result["leading_zero"] = self.leading_zero
        result["off_brake_duration"] = self.off_brake_duration
        result["swap_style"] = self.swap_style
        return result

    @classmethod
    def from_flat(cls, data: Dict[str, Any]) -> "BrakeTemperature":
        obj = cls()
        obj.name = data.get("name", obj.name)
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.bar = BarConfig.from_flat(data)
        obj.font = FontConfig.from_flat(data)
        obj.position = PositionConfig.from_flat(data)
        obj.average = CellConfig.from_flat(data, 'average')
        obj.degree_sign = CellConfig.from_flat(data, 'degree_sign')
        obj.temperature = CellConfig.from_flat(data, 'temperature')
        obj.average_sampling_duration = data.get("average_sampling_duration", obj.average_sampling_duration)
        obj.enable_heatmap_auto_matching = data.get("enable_heatmap_auto_matching", obj.enable_heatmap_auto_matching)
        obj.heatmap_name = data.get("heatmap_name", obj.heatmap_name)
        obj.leading_zero = data.get("leading_zero", obj.leading_zero)
        obj.off_brake_duration = data.get("off_brake_duration", obj.off_brake_duration)
        obj.swap_style = data.get("swap_style", obj.swap_style)
        return obj

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["bar"] = self.bar.to_dict()
        result["font"] = self.font.to_dict()
        result["position"] = self.position.to_dict()
        result["average"] = self.average.to_dict()
        result["degree_sign"] = self.degree_sign.to_dict()
        result["temperature"] = self.temperature.to_dict()
        result["average_sampling_duration"] = self.average_sampling_duration
        result["enable_heatmap_auto_matching"] = self.enable_heatmap_auto_matching
        result["heatmap_name"] = self.heatmap_name
        result["leading_zero"] = self.leading_zero
        result["off_brake_duration"] = self.off_brake_duration
        result["swap_style"] = self.swap_style
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BrakeTemperature":
        obj = cls()
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.bar = BarConfig.from_dict(data.get("bar", {}))
        obj.font = FontConfig.from_dict(data.get("font", {}))
        obj.position = PositionConfig.from_dict(data.get("position", {}))
        obj.average = CellConfig.from_dict(data.get("average", {}), 'average')
        obj.degree_sign = CellConfig.from_dict(data.get("degree_sign", {}), 'degree_sign')
        obj.temperature = CellConfig.from_dict(data.get("temperature", {}), 'temperature')
        obj.average_sampling_duration = data.get("average_sampling_duration", obj.average_sampling_duration)
        obj.enable_heatmap_auto_matching = data.get("enable_heatmap_auto_matching", obj.enable_heatmap_auto_matching)
        obj.heatmap_name = data.get("heatmap_name", obj.heatmap_name)
        obj.leading_zero = data.get("leading_zero", obj.leading_zero)
        obj.off_brake_duration = data.get("off_brake_duration", obj.off_brake_duration)
        obj.swap_style = data.get("swap_style", obj.swap_style)
        return obj
