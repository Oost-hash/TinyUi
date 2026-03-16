# Auto-generated widget
# Widget: fuel_energy_saver

from dataclasses import dataclass, field
from typing import Any, Dict

from ..base import BarConfig, CellConfig, FontConfig, PositionConfig, WidgetConfig
from ..colors import DARK_GRAY, DARK_GREEN, DARK_ORANGE, GREEN, LIGHT_INVERT, MID_GRAY, ORANGE


@dataclass
class FuelEnergySaver(WidgetConfig):
    name: str = "fuel_energy_saver"

    # base overrides
    bar_gap: int = 0
    update_interval: int = 100

    # groups
    bar: BarConfig = field(default_factory=lambda: BarConfig(bar_width=5))
    font: FontConfig = field(default_factory=FontConfig)
    position: PositionConfig = field(default_factory=lambda: PositionConfig(position_x=115, position_y=912))

    # cells
    consumption: CellConfig = field(default_factory=lambda: CellConfig(id='consumption', decimal_places=3))
    current_laps: CellConfig = field(default_factory=lambda: CellConfig(id='current_laps', font_color=DARK_GRAY.font_color, bkg_color=DARK_GRAY.bkg_color))
    delta: CellConfig = field(default_factory=lambda: CellConfig(id='delta', decimal_places=3))
    delta_consumption: CellConfig = field(default_factory=lambda: CellConfig(id='delta_consumption', font_color=LIGHT_INVERT.font_color, bkg_color=LIGHT_INVERT.bkg_color))
    lap_gain: CellConfig = field(default_factory=lambda: CellConfig(id='lap_gain', font_color=DARK_GREEN.font_color, bkg_color=DARK_GREEN.bkg_color))
    lap_loss: CellConfig = field(default_factory=lambda: CellConfig(id='lap_loss', font_color=DARK_ORANGE.font_color, bkg_color=DARK_ORANGE.bkg_color))
    target_consumption: CellConfig = field(default_factory=lambda: CellConfig(id='target_consumption', font_color=DARK_GRAY.font_color, bkg_color=DARK_GRAY.bkg_color))
    target_laps: CellConfig = field(default_factory=lambda: CellConfig(id='target_laps', font_color=MID_GRAY.font_color, bkg_color=MID_GRAY.bkg_color))

    # config
    enable_pit_entry_bias: bool = False
    minimum_reserve: float = 0.2
    number_of_less_laps: int = 0
    number_of_more_laps: int = 3
    remaining_pitstop_threshold: float = 0.1

    def to_flat(self) -> Dict[str, Any]:
        result = super().to_flat()
        result["name"] = self.name
        result["bar_gap"] = self.bar_gap
        result["update_interval"] = self.update_interval
        result.update(self.bar.to_flat())
        result.update(self.font.to_flat())
        result.update(self.position.to_flat())
        result.update(self.consumption.to_flat())
        result.update(self.current_laps.to_flat())
        result.update(self.delta.to_flat())
        result.update(self.delta_consumption.to_flat())
        result.update(self.lap_gain.to_flat())
        result.update(self.lap_loss.to_flat())
        result.update(self.target_consumption.to_flat())
        result.update(self.target_laps.to_flat())
        result["enable_pit_entry_bias"] = self.enable_pit_entry_bias
        result["minimum_reserve"] = self.minimum_reserve
        result["number_of_less_laps"] = self.number_of_less_laps
        result["number_of_more_laps"] = self.number_of_more_laps
        result["remaining_pitstop_threshold"] = self.remaining_pitstop_threshold
        return result

    @classmethod
    def from_flat(cls, data: Dict[str, Any]) -> "FuelEnergySaver":
        obj = cls()
        obj.name = data.get("name", obj.name)
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.bar_gap = data.get("bar_gap", obj.bar_gap)
        obj.update_interval = data.get("update_interval", obj.update_interval)
        obj.bar = BarConfig.from_flat(data)
        obj.font = FontConfig.from_flat(data)
        obj.position = PositionConfig.from_flat(data)
        obj.consumption = CellConfig.from_flat(data, 'consumption')
        obj.current_laps = CellConfig.from_flat(data, 'current_laps')
        obj.delta = CellConfig.from_flat(data, 'delta')
        obj.delta_consumption = CellConfig.from_flat(data, 'delta_consumption')
        obj.lap_gain = CellConfig.from_flat(data, 'lap_gain')
        obj.lap_loss = CellConfig.from_flat(data, 'lap_loss')
        obj.target_consumption = CellConfig.from_flat(data, 'target_consumption')
        obj.target_laps = CellConfig.from_flat(data, 'target_laps')
        obj.enable_pit_entry_bias = data.get("enable_pit_entry_bias", obj.enable_pit_entry_bias)
        obj.minimum_reserve = data.get("minimum_reserve", obj.minimum_reserve)
        obj.number_of_less_laps = data.get("number_of_less_laps", obj.number_of_less_laps)
        obj.number_of_more_laps = data.get("number_of_more_laps", obj.number_of_more_laps)
        obj.remaining_pitstop_threshold = data.get("remaining_pitstop_threshold", obj.remaining_pitstop_threshold)
        return obj

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["bar_gap"] = self.bar_gap
        result["update_interval"] = self.update_interval
        result["bar"] = self.bar.to_dict()
        result["font"] = self.font.to_dict()
        result["position"] = self.position.to_dict()
        result["consumption"] = self.consumption.to_dict()
        result["current_laps"] = self.current_laps.to_dict()
        result["delta"] = self.delta.to_dict()
        result["delta_consumption"] = self.delta_consumption.to_dict()
        result["lap_gain"] = self.lap_gain.to_dict()
        result["lap_loss"] = self.lap_loss.to_dict()
        result["target_consumption"] = self.target_consumption.to_dict()
        result["target_laps"] = self.target_laps.to_dict()
        result["enable_pit_entry_bias"] = self.enable_pit_entry_bias
        result["minimum_reserve"] = self.minimum_reserve
        result["number_of_less_laps"] = self.number_of_less_laps
        result["number_of_more_laps"] = self.number_of_more_laps
        result["remaining_pitstop_threshold"] = self.remaining_pitstop_threshold
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FuelEnergySaver":
        obj = cls()
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.bar_gap = data.get("bar_gap", obj.bar_gap)
        obj.update_interval = data.get("update_interval", obj.update_interval)
        obj.bar = BarConfig.from_dict(data.get("bar", {}))
        obj.font = FontConfig.from_dict(data.get("font", {}))
        obj.position = PositionConfig.from_dict(data.get("position", {}))
        obj.consumption = CellConfig.from_dict(data.get("consumption", {}), 'consumption')
        obj.current_laps = CellConfig.from_dict(data.get("current_laps", {}), 'current_laps')
        obj.delta = CellConfig.from_dict(data.get("delta", {}), 'delta')
        obj.delta_consumption = CellConfig.from_dict(data.get("delta_consumption", {}), 'delta_consumption')
        obj.lap_gain = CellConfig.from_dict(data.get("lap_gain", {}), 'lap_gain')
        obj.lap_loss = CellConfig.from_dict(data.get("lap_loss", {}), 'lap_loss')
        obj.target_consumption = CellConfig.from_dict(data.get("target_consumption", {}), 'target_consumption')
        obj.target_laps = CellConfig.from_dict(data.get("target_laps", {}), 'target_laps')
        obj.enable_pit_entry_bias = data.get("enable_pit_entry_bias", obj.enable_pit_entry_bias)
        obj.minimum_reserve = data.get("minimum_reserve", obj.minimum_reserve)
        obj.number_of_less_laps = data.get("number_of_less_laps", obj.number_of_less_laps)
        obj.number_of_more_laps = data.get("number_of_more_laps", obj.number_of_more_laps)
        obj.remaining_pitstop_threshold = data.get("remaining_pitstop_threshold", obj.remaining_pitstop_threshold)
        return obj
