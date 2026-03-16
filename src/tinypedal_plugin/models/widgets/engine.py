# Auto-generated widget
# Widget: engine

from dataclasses import dataclass, field
from typing import Any, Dict

from ..base import CellConfig, FontConfig, PositionConfig, WidgetConfig


@dataclass
class Engine(WidgetConfig):
    name: str = "engine"

    # groups
    font: FontConfig = field(default_factory=FontConfig)
    position: PositionConfig = field(default_factory=lambda: PositionConfig(position_x=57, position_y=293))

    # cells
    oil: CellConfig = field(default_factory=lambda: CellConfig(id='oil', column_index=1))
    oil_temperature: CellConfig = field(default_factory=lambda: CellConfig(id='oil_temperature'))
    power: CellConfig = field(default_factory=lambda: CellConfig(id='power', column_index=7))
    rpm: CellConfig = field(default_factory=lambda: CellConfig(id='rpm', column_index=4))
    rpm_maximum: CellConfig = field(default_factory=lambda: CellConfig(id='rpm_maximum', column_index=5))
    torque: CellConfig = field(default_factory=lambda: CellConfig(id='torque', column_index=6))
    turbo: CellConfig = field(default_factory=lambda: CellConfig(id='turbo', column_index=3))
    turbo_pressure: CellConfig = field(default_factory=lambda: CellConfig(id='turbo_pressure'))
    water: CellConfig = field(default_factory=lambda: CellConfig(id='water', column_index=2))
    water_temperature: CellConfig = field(default_factory=lambda: CellConfig(id='water_temperature'))

    # config
    overheat_threshold_oil: int = 110
    overheat_threshold_water: int = 110
    warning_color_overheat: str = '#FF2200'

    def to_flat(self) -> Dict[str, Any]:
        result = super().to_flat()
        result["name"] = self.name
        result.update(self.font.to_flat())
        result.update(self.position.to_flat())
        result.update(self.oil.to_flat())
        result.update(self.oil_temperature.to_flat())
        result.update(self.power.to_flat())
        result.update(self.rpm.to_flat())
        result.update(self.rpm_maximum.to_flat())
        result.update(self.torque.to_flat())
        result.update(self.turbo.to_flat())
        result.update(self.turbo_pressure.to_flat())
        result.update(self.water.to_flat())
        result.update(self.water_temperature.to_flat())
        result["overheat_threshold_oil"] = self.overheat_threshold_oil
        result["overheat_threshold_water"] = self.overheat_threshold_water
        result["warning_color_overheat"] = self.warning_color_overheat
        return result

    @classmethod
    def from_flat(cls, data: Dict[str, Any]) -> "Engine":
        obj = cls()
        obj.name = data.get("name", obj.name)
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.font = FontConfig.from_flat(data)
        obj.position = PositionConfig.from_flat(data)
        obj.oil = CellConfig.from_flat(data, 'oil')
        obj.oil_temperature = CellConfig.from_flat(data, 'oil_temperature')
        obj.power = CellConfig.from_flat(data, 'power')
        obj.rpm = CellConfig.from_flat(data, 'rpm')
        obj.rpm_maximum = CellConfig.from_flat(data, 'rpm_maximum')
        obj.torque = CellConfig.from_flat(data, 'torque')
        obj.turbo = CellConfig.from_flat(data, 'turbo')
        obj.turbo_pressure = CellConfig.from_flat(data, 'turbo_pressure')
        obj.water = CellConfig.from_flat(data, 'water')
        obj.water_temperature = CellConfig.from_flat(data, 'water_temperature')
        obj.overheat_threshold_oil = data.get("overheat_threshold_oil", obj.overheat_threshold_oil)
        obj.overheat_threshold_water = data.get("overheat_threshold_water", obj.overheat_threshold_water)
        obj.warning_color_overheat = data.get("warning_color_overheat", obj.warning_color_overheat)
        return obj

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["font"] = self.font.to_dict()
        result["position"] = self.position.to_dict()
        result["oil"] = self.oil.to_dict()
        result["oil_temperature"] = self.oil_temperature.to_dict()
        result["power"] = self.power.to_dict()
        result["rpm"] = self.rpm.to_dict()
        result["rpm_maximum"] = self.rpm_maximum.to_dict()
        result["torque"] = self.torque.to_dict()
        result["turbo"] = self.turbo.to_dict()
        result["turbo_pressure"] = self.turbo_pressure.to_dict()
        result["water"] = self.water.to_dict()
        result["water_temperature"] = self.water_temperature.to_dict()
        result["overheat_threshold_oil"] = self.overheat_threshold_oil
        result["overheat_threshold_water"] = self.overheat_threshold_water
        result["warning_color_overheat"] = self.warning_color_overheat
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Engine":
        obj = cls()
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.font = FontConfig.from_dict(data.get("font", {}))
        obj.position = PositionConfig.from_dict(data.get("position", {}))
        obj.oil = CellConfig.from_dict(data.get("oil", {}), 'oil')
        obj.oil_temperature = CellConfig.from_dict(data.get("oil_temperature", {}), 'oil_temperature')
        obj.power = CellConfig.from_dict(data.get("power", {}), 'power')
        obj.rpm = CellConfig.from_dict(data.get("rpm", {}), 'rpm')
        obj.rpm_maximum = CellConfig.from_dict(data.get("rpm_maximum", {}), 'rpm_maximum')
        obj.torque = CellConfig.from_dict(data.get("torque", {}), 'torque')
        obj.turbo = CellConfig.from_dict(data.get("turbo", {}), 'turbo')
        obj.turbo_pressure = CellConfig.from_dict(data.get("turbo_pressure", {}), 'turbo_pressure')
        obj.water = CellConfig.from_dict(data.get("water", {}), 'water')
        obj.water_temperature = CellConfig.from_dict(data.get("water_temperature", {}), 'water_temperature')
        obj.overheat_threshold_oil = data.get("overheat_threshold_oil", obj.overheat_threshold_oil)
        obj.overheat_threshold_water = data.get("overheat_threshold_water", obj.overheat_threshold_water)
        obj.warning_color_overheat = data.get("warning_color_overheat", obj.warning_color_overheat)
        return obj
