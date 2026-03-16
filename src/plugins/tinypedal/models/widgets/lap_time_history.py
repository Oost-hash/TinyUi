# Auto-generated widget
# Widget: lap_time_history

from dataclasses import dataclass, field
from typing import Any, Dict

from ..base import CellConfig, FontConfig, PositionConfig, WidgetConfig
from ..colors import HISTORY_LAST, HISTORY_LAST_DIM, HISTORY_PRIMARY, HISTORY_SECONDARY, ORANGE, SECONDARY


@dataclass
class LapTimeHistory(WidgetConfig):
    name: str = "lap_time_history"

    # base overrides
    bar_gap: int = 1

    # groups
    font: FontConfig = field(default_factory=FontConfig)
    position: PositionConfig = field(default_factory=lambda: PositionConfig(position_x=523, position_y=393))

    # cells
    delta: CellConfig = field(default_factory=lambda: CellConfig(id='delta', font_color=HISTORY_PRIMARY.font_color, bkg_color=HISTORY_PRIMARY.bkg_color, column_index=3))
    empty_history: CellConfig = field(default_factory=lambda: CellConfig(id='empty_history', show=False))
    fuel: CellConfig = field(default_factory=lambda: CellConfig(id='fuel', font_color=HISTORY_SECONDARY.font_color, bkg_color=HISTORY_SECONDARY.bkg_color, column_index=4))
    fuel_sign: CellConfig = field(default_factory=lambda: CellConfig(id='fuel_sign'))
    invalid_laptime: CellConfig = field(default_factory=lambda: CellConfig(id='invalid_laptime', font_color=ORANGE.font_color, bkg_color=ORANGE.bkg_color))
    laps: CellConfig = field(default_factory=lambda: CellConfig(id='laps', font_color=HISTORY_SECONDARY.font_color, bkg_color=HISTORY_SECONDARY.bkg_color, column_index=1))
    last_delta: CellConfig = field(default_factory=lambda: CellConfig(id='last_delta', font_color=HISTORY_LAST.font_color, bkg_color=HISTORY_LAST.bkg_color))
    last_fuel: CellConfig = field(default_factory=lambda: CellConfig(id='last_fuel', font_color=HISTORY_LAST_DIM.font_color, bkg_color=HISTORY_LAST_DIM.bkg_color))
    last_laps: CellConfig = field(default_factory=lambda: CellConfig(id='last_laps', font_color=HISTORY_LAST_DIM.font_color, bkg_color=HISTORY_LAST_DIM.bkg_color))
    last_time: CellConfig = field(default_factory=lambda: CellConfig(id='last_time', font_color=HISTORY_LAST.font_color, bkg_color=HISTORY_LAST.bkg_color))
    last_wear: CellConfig = field(default_factory=lambda: CellConfig(id='last_wear', font_color=HISTORY_LAST.font_color, bkg_color=HISTORY_LAST.bkg_color))
    time: CellConfig = field(default_factory=lambda: CellConfig(id='time', font_color=HISTORY_PRIMARY.font_color, bkg_color=HISTORY_PRIMARY.bkg_color, column_index=2))
    virtual_energy_if_available: CellConfig = field(default_factory=lambda: CellConfig(id='virtual_energy_if_available'))
    wear: CellConfig = field(default_factory=lambda: CellConfig(id='wear', font_color=HISTORY_PRIMARY.font_color, bkg_color=HISTORY_PRIMARY.bkg_color, column_index=5))
    wear_sign: CellConfig = field(default_factory=lambda: CellConfig(id='wear_sign'))

    # config
    delta_decimal_places: int = 2
    fuel_decimal_places: int = 2
    lap_time_history_count: int = 10
    wear_decimal_places: int = 1

    def to_flat(self) -> Dict[str, Any]:
        result = super().to_flat()
        result["name"] = self.name
        result["bar_gap"] = self.bar_gap
        result.update(self.font.to_flat())
        result.update(self.position.to_flat())
        result.update(self.delta.to_flat())
        result.update(self.empty_history.to_flat())
        result.update(self.fuel.to_flat())
        result.update(self.fuel_sign.to_flat())
        result.update(self.invalid_laptime.to_flat())
        result.update(self.laps.to_flat())
        result.update(self.last_delta.to_flat())
        result.update(self.last_fuel.to_flat())
        result.update(self.last_laps.to_flat())
        result.update(self.last_time.to_flat())
        result.update(self.last_wear.to_flat())
        result.update(self.time.to_flat())
        result.update(self.virtual_energy_if_available.to_flat())
        result.update(self.wear.to_flat())
        result.update(self.wear_sign.to_flat())
        result["delta_decimal_places"] = self.delta_decimal_places
        result["fuel_decimal_places"] = self.fuel_decimal_places
        result["lap_time_history_count"] = self.lap_time_history_count
        result["wear_decimal_places"] = self.wear_decimal_places
        return result

    @classmethod
    def from_flat(cls, data: Dict[str, Any]) -> "LapTimeHistory":
        obj = cls()
        obj.name = data.get("name", obj.name)
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.bar_gap = data.get("bar_gap", obj.bar_gap)
        obj.font = FontConfig.from_flat(data)
        obj.position = PositionConfig.from_flat(data)
        obj.delta = CellConfig.from_flat(data, 'delta')
        obj.empty_history = CellConfig.from_flat(data, 'empty_history')
        obj.fuel = CellConfig.from_flat(data, 'fuel')
        obj.fuel_sign = CellConfig.from_flat(data, 'fuel_sign')
        obj.invalid_laptime = CellConfig.from_flat(data, 'invalid_laptime')
        obj.laps = CellConfig.from_flat(data, 'laps')
        obj.last_delta = CellConfig.from_flat(data, 'last_delta')
        obj.last_fuel = CellConfig.from_flat(data, 'last_fuel')
        obj.last_laps = CellConfig.from_flat(data, 'last_laps')
        obj.last_time = CellConfig.from_flat(data, 'last_time')
        obj.last_wear = CellConfig.from_flat(data, 'last_wear')
        obj.time = CellConfig.from_flat(data, 'time')
        obj.virtual_energy_if_available = CellConfig.from_flat(data, 'virtual_energy_if_available')
        obj.wear = CellConfig.from_flat(data, 'wear')
        obj.wear_sign = CellConfig.from_flat(data, 'wear_sign')
        obj.delta_decimal_places = data.get("delta_decimal_places", obj.delta_decimal_places)
        obj.fuel_decimal_places = data.get("fuel_decimal_places", obj.fuel_decimal_places)
        obj.lap_time_history_count = data.get("lap_time_history_count", obj.lap_time_history_count)
        obj.wear_decimal_places = data.get("wear_decimal_places", obj.wear_decimal_places)
        return obj

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["bar_gap"] = self.bar_gap
        result["font"] = self.font.to_dict()
        result["position"] = self.position.to_dict()
        result["delta"] = self.delta.to_dict()
        result["empty_history"] = self.empty_history.to_dict()
        result["fuel"] = self.fuel.to_dict()
        result["fuel_sign"] = self.fuel_sign.to_dict()
        result["invalid_laptime"] = self.invalid_laptime.to_dict()
        result["laps"] = self.laps.to_dict()
        result["last_delta"] = self.last_delta.to_dict()
        result["last_fuel"] = self.last_fuel.to_dict()
        result["last_laps"] = self.last_laps.to_dict()
        result["last_time"] = self.last_time.to_dict()
        result["last_wear"] = self.last_wear.to_dict()
        result["time"] = self.time.to_dict()
        result["virtual_energy_if_available"] = self.virtual_energy_if_available.to_dict()
        result["wear"] = self.wear.to_dict()
        result["wear_sign"] = self.wear_sign.to_dict()
        result["delta_decimal_places"] = self.delta_decimal_places
        result["fuel_decimal_places"] = self.fuel_decimal_places
        result["lap_time_history_count"] = self.lap_time_history_count
        result["wear_decimal_places"] = self.wear_decimal_places
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LapTimeHistory":
        obj = cls()
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.bar_gap = data.get("bar_gap", obj.bar_gap)
        obj.font = FontConfig.from_dict(data.get("font", {}))
        obj.position = PositionConfig.from_dict(data.get("position", {}))
        obj.delta = CellConfig.from_dict(data.get("delta", {}), 'delta')
        obj.empty_history = CellConfig.from_dict(data.get("empty_history", {}), 'empty_history')
        obj.fuel = CellConfig.from_dict(data.get("fuel", {}), 'fuel')
        obj.fuel_sign = CellConfig.from_dict(data.get("fuel_sign", {}), 'fuel_sign')
        obj.invalid_laptime = CellConfig.from_dict(data.get("invalid_laptime", {}), 'invalid_laptime')
        obj.laps = CellConfig.from_dict(data.get("laps", {}), 'laps')
        obj.last_delta = CellConfig.from_dict(data.get("last_delta", {}), 'last_delta')
        obj.last_fuel = CellConfig.from_dict(data.get("last_fuel", {}), 'last_fuel')
        obj.last_laps = CellConfig.from_dict(data.get("last_laps", {}), 'last_laps')
        obj.last_time = CellConfig.from_dict(data.get("last_time", {}), 'last_time')
        obj.last_wear = CellConfig.from_dict(data.get("last_wear", {}), 'last_wear')
        obj.time = CellConfig.from_dict(data.get("time", {}), 'time')
        obj.virtual_energy_if_available = CellConfig.from_dict(data.get("virtual_energy_if_available", {}), 'virtual_energy_if_available')
        obj.wear = CellConfig.from_dict(data.get("wear", {}), 'wear')
        obj.wear_sign = CellConfig.from_dict(data.get("wear_sign", {}), 'wear_sign')
        obj.delta_decimal_places = data.get("delta_decimal_places", obj.delta_decimal_places)
        obj.fuel_decimal_places = data.get("fuel_decimal_places", obj.fuel_decimal_places)
        obj.lap_time_history_count = data.get("lap_time_history_count", obj.lap_time_history_count)
        obj.wear_decimal_places = data.get("wear_decimal_places", obj.wear_decimal_places)
        return obj
