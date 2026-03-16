# Auto-generated widget
# Widget: stint_history

from dataclasses import dataclass, field
from typing import Any, Dict

from ..base import CellConfig, FontConfig, PositionConfig, WidgetConfig
from ..colors import HISTORY_LAST, HISTORY_LAST_DIM, HISTORY_PRIMARY, HISTORY_SECONDARY, SECONDARY


@dataclass
class StintHistory(WidgetConfig):
    name: str = "stint_history"

    # base overrides
    bar_gap: int = 1

    # groups
    font: FontConfig = field(default_factory=FontConfig)
    position: PositionConfig = field(default_factory=lambda: PositionConfig(position_x=523, position_y=423))

    # cells
    consistency: CellConfig = field(default_factory=lambda: CellConfig(id='consistency', font_color=HISTORY_SECONDARY.font_color, bkg_color=HISTORY_SECONDARY.bkg_color, column_index=7))
    consistency_sign: CellConfig = field(default_factory=lambda: CellConfig(id='consistency_sign'))
    delta: CellConfig = field(default_factory=lambda: CellConfig(id='delta', font_color=HISTORY_PRIMARY.font_color, bkg_color=HISTORY_PRIMARY.bkg_color, column_index=6))
    empty_history: CellConfig = field(default_factory=lambda: CellConfig(id='empty_history', show=False))
    fuel: CellConfig = field(default_factory=lambda: CellConfig(id='fuel', font_color=HISTORY_SECONDARY.font_color, bkg_color=HISTORY_SECONDARY.bkg_color, column_index=3))
    fuel_sign: CellConfig = field(default_factory=lambda: CellConfig(id='fuel_sign'))
    laps: CellConfig = field(default_factory=lambda: CellConfig(id='laps', font_color=HISTORY_SECONDARY.font_color, bkg_color=HISTORY_SECONDARY.bkg_color, column_index=1))
    last_stint_consistency: CellConfig = field(default_factory=lambda: CellConfig(id='last_stint_consistency', font_color=HISTORY_LAST_DIM.font_color, bkg_color=HISTORY_LAST_DIM.bkg_color))
    last_stint_delta: CellConfig = field(default_factory=lambda: CellConfig(id='last_stint_delta', font_color=HISTORY_LAST.font_color, bkg_color=HISTORY_LAST.bkg_color))
    last_stint_fuel: CellConfig = field(default_factory=lambda: CellConfig(id='last_stint_fuel', font_color=HISTORY_LAST_DIM.font_color, bkg_color=HISTORY_LAST_DIM.bkg_color))
    last_stint_laps: CellConfig = field(default_factory=lambda: CellConfig(id='last_stint_laps', font_color=HISTORY_LAST_DIM.font_color, bkg_color=HISTORY_LAST_DIM.bkg_color))
    last_stint_time: CellConfig = field(default_factory=lambda: CellConfig(id='last_stint_time', font_color=HISTORY_LAST.font_color, bkg_color=HISTORY_LAST.bkg_color))
    last_stint_tyre: CellConfig = field(default_factory=lambda: CellConfig(id='last_stint_tyre', font_color=HISTORY_LAST.font_color, bkg_color=HISTORY_LAST.bkg_color))
    last_stint_wear: CellConfig = field(default_factory=lambda: CellConfig(id='last_stint_wear', font_color=HISTORY_LAST_DIM.font_color, bkg_color=HISTORY_LAST_DIM.bkg_color))
    time: CellConfig = field(default_factory=lambda: CellConfig(id='time', font_color=HISTORY_PRIMARY.font_color, bkg_color=HISTORY_PRIMARY.bkg_color, column_index=2))
    tyre: CellConfig = field(default_factory=lambda: CellConfig(id='tyre', font_color=HISTORY_PRIMARY.font_color, bkg_color=HISTORY_PRIMARY.bkg_color, column_index=4))
    virtual_energy_if_available: CellConfig = field(default_factory=lambda: CellConfig(id='virtual_energy_if_available'))
    wear: CellConfig = field(default_factory=lambda: CellConfig(id='wear', font_color=HISTORY_SECONDARY.font_color, bkg_color=HISTORY_SECONDARY.bkg_color, column_index=5))
    wear_sign: CellConfig = field(default_factory=lambda: CellConfig(id='wear_sign'))

    # config
    consistency_decimal_places: int = 2
    delta_decimal_places: int = 2
    fuel_decimal_places: int = 3
    stint_history_count: int = 2
    wear_decimal_places: int = 2

    def to_flat(self) -> Dict[str, Any]:
        result = super().to_flat()
        result["name"] = self.name
        result["bar_gap"] = self.bar_gap
        result.update(self.font.to_flat())
        result.update(self.position.to_flat())
        result.update(self.consistency.to_flat())
        result.update(self.consistency_sign.to_flat())
        result.update(self.delta.to_flat())
        result.update(self.empty_history.to_flat())
        result.update(self.fuel.to_flat())
        result.update(self.fuel_sign.to_flat())
        result.update(self.laps.to_flat())
        result.update(self.last_stint_consistency.to_flat())
        result.update(self.last_stint_delta.to_flat())
        result.update(self.last_stint_fuel.to_flat())
        result.update(self.last_stint_laps.to_flat())
        result.update(self.last_stint_time.to_flat())
        result.update(self.last_stint_tyre.to_flat())
        result.update(self.last_stint_wear.to_flat())
        result.update(self.time.to_flat())
        result.update(self.tyre.to_flat())
        result.update(self.virtual_energy_if_available.to_flat())
        result.update(self.wear.to_flat())
        result.update(self.wear_sign.to_flat())
        result["consistency_decimal_places"] = self.consistency_decimal_places
        result["delta_decimal_places"] = self.delta_decimal_places
        result["fuel_decimal_places"] = self.fuel_decimal_places
        result["stint_history_count"] = self.stint_history_count
        result["wear_decimal_places"] = self.wear_decimal_places
        return result

    @classmethod
    def from_flat(cls, data: Dict[str, Any]) -> "StintHistory":
        obj = cls()
        obj.name = data.get("name", obj.name)
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.bar_gap = data.get("bar_gap", obj.bar_gap)
        obj.font = FontConfig.from_flat(data)
        obj.position = PositionConfig.from_flat(data)
        obj.consistency = CellConfig.from_flat(data, 'consistency')
        obj.consistency_sign = CellConfig.from_flat(data, 'consistency_sign')
        obj.delta = CellConfig.from_flat(data, 'delta')
        obj.empty_history = CellConfig.from_flat(data, 'empty_history')
        obj.fuel = CellConfig.from_flat(data, 'fuel')
        obj.fuel_sign = CellConfig.from_flat(data, 'fuel_sign')
        obj.laps = CellConfig.from_flat(data, 'laps')
        obj.last_stint_consistency = CellConfig.from_flat(data, 'last_stint_consistency')
        obj.last_stint_delta = CellConfig.from_flat(data, 'last_stint_delta')
        obj.last_stint_fuel = CellConfig.from_flat(data, 'last_stint_fuel')
        obj.last_stint_laps = CellConfig.from_flat(data, 'last_stint_laps')
        obj.last_stint_time = CellConfig.from_flat(data, 'last_stint_time')
        obj.last_stint_tyre = CellConfig.from_flat(data, 'last_stint_tyre')
        obj.last_stint_wear = CellConfig.from_flat(data, 'last_stint_wear')
        obj.time = CellConfig.from_flat(data, 'time')
        obj.tyre = CellConfig.from_flat(data, 'tyre')
        obj.virtual_energy_if_available = CellConfig.from_flat(data, 'virtual_energy_if_available')
        obj.wear = CellConfig.from_flat(data, 'wear')
        obj.wear_sign = CellConfig.from_flat(data, 'wear_sign')
        obj.consistency_decimal_places = data.get("consistency_decimal_places", obj.consistency_decimal_places)
        obj.delta_decimal_places = data.get("delta_decimal_places", obj.delta_decimal_places)
        obj.fuel_decimal_places = data.get("fuel_decimal_places", obj.fuel_decimal_places)
        obj.stint_history_count = data.get("stint_history_count", obj.stint_history_count)
        obj.wear_decimal_places = data.get("wear_decimal_places", obj.wear_decimal_places)
        return obj

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["bar_gap"] = self.bar_gap
        result["font"] = self.font.to_dict()
        result["position"] = self.position.to_dict()
        result["consistency"] = self.consistency.to_dict()
        result["consistency_sign"] = self.consistency_sign.to_dict()
        result["delta"] = self.delta.to_dict()
        result["empty_history"] = self.empty_history.to_dict()
        result["fuel"] = self.fuel.to_dict()
        result["fuel_sign"] = self.fuel_sign.to_dict()
        result["laps"] = self.laps.to_dict()
        result["last_stint_consistency"] = self.last_stint_consistency.to_dict()
        result["last_stint_delta"] = self.last_stint_delta.to_dict()
        result["last_stint_fuel"] = self.last_stint_fuel.to_dict()
        result["last_stint_laps"] = self.last_stint_laps.to_dict()
        result["last_stint_time"] = self.last_stint_time.to_dict()
        result["last_stint_tyre"] = self.last_stint_tyre.to_dict()
        result["last_stint_wear"] = self.last_stint_wear.to_dict()
        result["time"] = self.time.to_dict()
        result["tyre"] = self.tyre.to_dict()
        result["virtual_energy_if_available"] = self.virtual_energy_if_available.to_dict()
        result["wear"] = self.wear.to_dict()
        result["wear_sign"] = self.wear_sign.to_dict()
        result["consistency_decimal_places"] = self.consistency_decimal_places
        result["delta_decimal_places"] = self.delta_decimal_places
        result["fuel_decimal_places"] = self.fuel_decimal_places
        result["stint_history_count"] = self.stint_history_count
        result["wear_decimal_places"] = self.wear_decimal_places
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StintHistory":
        obj = cls()
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.bar_gap = data.get("bar_gap", obj.bar_gap)
        obj.font = FontConfig.from_dict(data.get("font", {}))
        obj.position = PositionConfig.from_dict(data.get("position", {}))
        obj.consistency = CellConfig.from_dict(data.get("consistency", {}), 'consistency')
        obj.consistency_sign = CellConfig.from_dict(data.get("consistency_sign", {}), 'consistency_sign')
        obj.delta = CellConfig.from_dict(data.get("delta", {}), 'delta')
        obj.empty_history = CellConfig.from_dict(data.get("empty_history", {}), 'empty_history')
        obj.fuel = CellConfig.from_dict(data.get("fuel", {}), 'fuel')
        obj.fuel_sign = CellConfig.from_dict(data.get("fuel_sign", {}), 'fuel_sign')
        obj.laps = CellConfig.from_dict(data.get("laps", {}), 'laps')
        obj.last_stint_consistency = CellConfig.from_dict(data.get("last_stint_consistency", {}), 'last_stint_consistency')
        obj.last_stint_delta = CellConfig.from_dict(data.get("last_stint_delta", {}), 'last_stint_delta')
        obj.last_stint_fuel = CellConfig.from_dict(data.get("last_stint_fuel", {}), 'last_stint_fuel')
        obj.last_stint_laps = CellConfig.from_dict(data.get("last_stint_laps", {}), 'last_stint_laps')
        obj.last_stint_time = CellConfig.from_dict(data.get("last_stint_time", {}), 'last_stint_time')
        obj.last_stint_tyre = CellConfig.from_dict(data.get("last_stint_tyre", {}), 'last_stint_tyre')
        obj.last_stint_wear = CellConfig.from_dict(data.get("last_stint_wear", {}), 'last_stint_wear')
        obj.time = CellConfig.from_dict(data.get("time", {}), 'time')
        obj.tyre = CellConfig.from_dict(data.get("tyre", {}), 'tyre')
        obj.virtual_energy_if_available = CellConfig.from_dict(data.get("virtual_energy_if_available", {}), 'virtual_energy_if_available')
        obj.wear = CellConfig.from_dict(data.get("wear", {}), 'wear')
        obj.wear_sign = CellConfig.from_dict(data.get("wear_sign", {}), 'wear_sign')
        obj.consistency_decimal_places = data.get("consistency_decimal_places", obj.consistency_decimal_places)
        obj.delta_decimal_places = data.get("delta_decimal_places", obj.delta_decimal_places)
        obj.fuel_decimal_places = data.get("fuel_decimal_places", obj.fuel_decimal_places)
        obj.stint_history_count = data.get("stint_history_count", obj.stint_history_count)
        obj.wear_decimal_places = data.get("wear_decimal_places", obj.wear_decimal_places)
        return obj
